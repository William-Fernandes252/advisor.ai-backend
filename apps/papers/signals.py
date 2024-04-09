from apps.papers import models
from apps.papers.tasks import update_papers_position_embeddings


def recalculate_papers_embeddings_on_delete(
    sender: type[models.Paper], *args, **kwargs
):
    """Updates the paper embeddings when a paper is deleted.

    This is necessary to keep the embeddings in sync with the papers data,
    as deletions create gaps on the positions, which can compromise the
    value and quality of suggestions.
    """
    update_papers_position_embeddings()


def recalculate_papers_embeddings_on_save(
    sender: type[models.Paper], instance: models.Paper, created, *args, **kwargs
):
    """Updates the paper embeddings when a paper is saved."""
    if created and instance.pk:
        update_papers_position_embeddings()
