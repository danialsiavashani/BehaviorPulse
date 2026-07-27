import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.models.client_app import ClientApp
from app.db.models.observation_analysis import ObservationAnalysis
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.observation_analysis import ObservationAnalysisDetail, ObservationAnalysisListItem
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/v1/analyses", tags=["analyses"])


@router.get("", response_model=PaginatedResponse[ObservationAnalysisListItem])
def list_analyses(
    client_app_id: uuid.UUID | None = Query(default=None),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = (
        select(
            ObservationAnalysis.id,
            ObservationAnalysis.analysis_id,
            ObservationAnalysis.client_app_id,
            ClientApp.name.label("app_name"),
            ObservationAnalysis.subject_type,
            ObservationAnalysis.subject_label,
            ObservationAnalysis.total_observations,
            ObservationAnalysis.computed_confidence,
            ObservationAnalysis.summary,
            ObservationAnalysis.created_at,
        )
        .join(ClientApp, ObservationAnalysis.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == current_user.id)
    )

    if client_app_id is not None:
        base_query = base_query.where(ObservationAnalysis.client_app_id == client_app_id)

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    rows = db.execute(
        base_query.order_by(ObservationAnalysis.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()

    items = [
        ObservationAnalysisListItem(
            id=row.id,
            analysis_id=row.analysis_id,
            client_app_id=row.client_app_id,
            app_name=row.app_name,
            subject_type=row.subject_type,
            subject_label=row.subject_label,
            total_observations=row.total_observations,
            computed_confidence=row.computed_confidence,
            summary=row.summary,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{analysis_id}", response_model=ObservationAnalysisDetail)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = db.scalar(
        select(ObservationAnalysis).where(ObservationAnalysis.analysis_id == analysis_id)
    )
    if analysis is None:
        raise AppError("not_found", "Analysis not found.", 404)

    client_app = db.get(ClientApp, analysis.client_app_id)
    if client_app is None or client_app.owner_user_id != current_user.id:
        raise AppError("not_found", "Analysis not found.", 404)

    return ObservationAnalysisDetail(
        id=analysis.id,
        analysis_id=analysis.analysis_id,
        client_app_id=analysis.client_app_id,
        app_name=client_app.name,
        subject_type=analysis.subject_type,
        subject_label=analysis.subject_label,
        total_observations=analysis.total_observations,
        computed_confidence=analysis.computed_confidence,
        summary=analysis.summary,
        prediction=analysis.prediction,
        pattern_table=analysis.pattern_table_json,
        computed_metrics=analysis.computed_metrics_json,
        recommendations=analysis.recommendations_json,
        warnings=analysis.warnings_json,
        created_at=analysis.created_at,
    )