from dataclasses import dataclass
from typing import Any, List, Optional

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.models.common.pagination import PagedResponseSchema, paginate
from app.repositories.base_repository import BaseRepository

class ImageUploadHistoryRepository(
    BaseRepository[VocabularyPrompt, VocabularyPromptCreate, Any]
):
    def create_with_category(
        self, prompt_create: VocabularyPromptCreate, user_id: str
    ) -> CreateWithCategoryResponse:
        self.logger.debug("Create voca lesson with category")
        with self.session_factory() as session:
            stmt = (
                insert(Category)
                .values(category_name=prompt_create.category, user_id=user_id)
                .on_conflict_do_update(
                    index_elements=["category_name", "user_id"],
                    set_={"category_name": prompt_create.category},
                )
                .returning(Category.id)
            )
            result = session.execute(stmt)
            insert_id = result.fetchone()[0]

            learning_language_id = check_language(
                session, prompt_create.learning_language
            )
            translated_language_id = check_language(
                session, prompt_create.translated_language
            )

            difficult_level_id = check_difficulty_lesson(
                session, prompt_create.difficulty_level
            )

            prompt_obj = VocabularyPrompt(
                prompt=prompt_create.prompt,
                category_id=insert_id,
                difficulty_level_id=difficult_level_id,
                language_id=learning_language_id,
            )

            translated_prompt_obj = VocabularyPromptTranslation(
                translated_language_id=translated_language_id,
                translated_text=prompt_create.translation,
                prompt=prompt_obj,
            )

            session.add(prompt_obj)
            session.add(translated_prompt_obj)

            questions_with_answers = parse_question_answers(
                prompt_obj,
                prompt_create,
                learning_language_id,
                translated_language_id,
            )

            session.add_all(questions_with_answers.questions)
            session.add_all(questions_with_answers.answers)
            session.commit()

            return CreateWithCategoryResponse(
                insert_id, prompt_create.learning_language
            )

    def get_history_questions(
        self,
        question_input: GetVocabularyHistoryQuestion,
        user_id: str,
        page: int,
        size: int,
    ) -> PagedResponseSchema[VocabularyPrompt]:
        with self.session_factory() as session:
            query = (
                session.query(VocabularyPrompt)
                .join(Category)
                .join(Language)
                .join(DifficultyLevels)
                .options(
                    joinedload(VocabularyPrompt.language),
                    joinedload(VocabularyPrompt.difficulty_level),
                    joinedload(VocabularyPrompt.translations).joinedload(
                        VocabularyPromptTranslation.translated_language
                    ),
                    joinedload(VocabularyPrompt.questions).options(
                        joinedload(VocabularyQuestion.translations),
                        joinedload(VocabularyQuestion.answers).joinedload(
                            VocabularyAnswer.translations
                        ),
                    ),
                )
                .filter(
                    and_(
                        Category.id == question_input.category_id,
                        Category.user_id == user_id,
                        Language.language_name
                        == question_input.learning_language.upper(),
                        VocabularyPrompt.is_valid,
                    )
                )
                .order_by(VocabularyPrompt.created_at.desc())
            )
            return paginate(page, size, query)


class InvalidLanguage(Exception):
    def __init__(self, language: str):
        super().__init__(f"Invalid language name: {language} !!!")


class InvalidLessonLevel(Exception):
    def __init__(self, language: str):
        super().__init__(f"Invalid lesson level: {language} !!!")
