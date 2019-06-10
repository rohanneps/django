
from celery.decorators import task
from core.start import start_core
from .models import ProjectComparator


@task(name="core_computation")
def comparator_comparision(project_comparison_id):
    start_core(project_comparison_id)



