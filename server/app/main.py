import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.template import main as template_router
from util.env import get_env

# get environment mode
env_mode = get_env("ENV_MODE", "development")

# logger config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if env_mode == "development":
    logger.setLevel(level=logging.DEBUG)

# production時，docsを表示しない
app_params = {}
if env_mode == "production":
    app_params["docs_url"] = None
    app_params["redoc_url"] = None
    app_params["openapi_url"] = None

# create app
app = FastAPI(**app_params)

origins = [
    "http://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static folder
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# add routers
app.include_router(
    template_router.router,
    prefix="/template"
)
