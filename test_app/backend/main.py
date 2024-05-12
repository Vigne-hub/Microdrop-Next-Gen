from fastapi import FastAPI, HTTPException
from worker import process_task, process_advanced_task
from typing import Optional

app = FastAPI()


@app.post("/tasks/")
async def create_task(task_type: str, parameters: Optional[dict] = None):
    try:
        if task_type in ['set_hv', 'set_frequency']:
            process_task.send(task_type, parameters or {})
        elif task_type == 'advanced_operation':
            process_advanced_task.send(task_type, parameters or {})
        else:
            raise ValueError("Unsupported task type")

        return {"message": "Task sent to queue", "task_type": task_type, "parameters": parameters}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
