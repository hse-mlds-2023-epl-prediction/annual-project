from pydantic import BaseModel, Field

class CatBoostParams(BaseModel):
    iterations: int
    depth: int
    learning_rate: float
    l2_leaf_reg: float
    random_strength: float
    bagging_temperature: float
    border_count: int
    leaf_estimation_iterations: int
    loss_function: str
    task_type: str
    random_seed: int
    verbose: bool