import os
import uvicorn

if __name__ == '__main__':
    uvicorn.run('proxy.api:app',
                host="0.0.0.0",
                port=int(os.environ.get('UVICORN_PORT', 8000)),
                log_level='info')
