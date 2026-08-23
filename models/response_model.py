from pydantic import BaseModel

class PostResponse(BaseModel):
    message: str

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'message':'Star added successfully!',
                    'status': '201',
                    'token': 'Your Token'
                }
            ]
        }
    }

class PutResponse(BaseModel):
    message: str

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'message': 'Star updated successfully!',
                    'status': '200',
                    'token': 'Your Token'
                }
            ]
        }
    }

class DeleteResponse(BaseModel):
    message: str
    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'message': 'Star deleted successfully!',
                    'status': '200',
                    'token': 'Your Token'
                }
            ]
        }
    }