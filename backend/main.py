"""API routes for the AI Crypto Advisor backend."""

# --- Imports ---

from fastapi import Depends, FastAPI, HTTPException  # the app itself, DI, error responses
from fastapi.middleware.cors import CORSMiddleware  # lets the frontend call this backend
from sqlalchemy import select, text, func  # builds queries; raw SQL; DB-side functions
from sqlalchemy.dialects.postgresql import insert as postgres_insert  # Postgres-specific upsert
from sqlalchemy.exc import IntegrityError  # the error a broken DB constraint raises
from sqlalchemy.orm import Session  # works with model objects (add/commit/query)

from auth import pwd_context, create_token, get_current_user
from database import engine, Base
from schemas import SignupRequest, LoginRequest, QuizAnswers, VoteRequest
from tables import User, Vote
from services.prices import get_prices
from services.news import get_news
from services.memes import get_meme
from services.insight import get_daily_insight


# --- Setup ---

app = FastAPI()

# lets the frontend (localhost:5173) call this backend from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# creates every table from tables.py in Postgres if it doesn't exist yet
Base.metadata.create_all(engine)


# --- Endpoints ---

@app.get("/health")
def health_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {"result": result.scalar()}


@app.post("/signup")
def signup(request: SignupRequest):
    password_hash = pwd_context.hash(request.password)
    new_user = User(
        email=request.email,
        name=request.name,
        password_hash=password_hash,
    )
    with Session(engine) as session:
        session.add(new_user)
        try:
            session.commit()
        except IntegrityError:
            # unique constraint on email caught a duplicate signup
            raise HTTPException(status_code=400, detail="Email already taken")
        # Postgres generates the id, so it's only readable after the commit
        token = create_token(new_user.id)
    return {"message": "Account created", "token": token}


@app.post("/login")
def login(request: LoginRequest):
    with Session(engine) as session:
        user = session.scalars(
            select(User).where(User.email == request.email)
        ).first()

    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"token": create_token(user.id)}


@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "coins": current_user.coins,
        "investor_type": current_user.investor_type,
        "content_types": current_user.content_types,
    }


@app.post("/onboarding")
def onboarding(
    request: QuizAnswers,
    current_user: User = Depends(get_current_user),
):
    with Session(engine) as session:
        # re-fetch inside this session so SQLAlchemy tracks the changes below
        user = session.get(User, current_user.id)
        user.coins = request.coins
        user.investor_type = request.investor_type
        user.content_types = request.content_types
        # writes the three changes above to Postgres, as one all-or-nothing transaction
        session.commit()
    return {"message": "Preferences saved"}


@app.post("/vote")
def vote(
    request: VoteRequest,
    current_user: User = Depends(get_current_user),
):
    with Session(engine) as session:
        insert_stmt = postgres_insert(Vote).values(
            user_id=current_user.id,
            section=request.section,
            topic=request.topic,
            item=request.item,
            direction=request.direction,
        )
        # if today's row for this user+section+item already exists, overwrite
        # its direction with whatever was just clicked, instead of a second
        # row — see tables.py's index for what counts as "already exists"
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[
                Vote.user_id,
                Vote.section,
                Vote.item,
                func.date(Vote.created_at),
            ],
            set_={"direction": insert_stmt.excluded.direction},
        )
        session.execute(upsert_stmt)
        session.commit()
    return {"message": "Vote recorded"}


@app.get("/votes")
def my_votes(current_user: User = Depends(get_current_user)):
    """Every item this user has voted on, as {section: {item: direction}}."""
    with Session(engine) as session:
        rows = session.scalars(
            select(Vote)
            .where(Vote.user_id == current_user.id)
            # oldest first, so a later vote on the same item overwrites an
            # earlier one below and the newest opinion is what survives
            .order_by(Vote.created_at)
        ).all()

    votes = {}
    for row in rows:
        votes.setdefault(row.section, {})[row.item] = row.direction
    return votes


@app.get("/dashboard/prices")
def dashboard_prices(current_user: User = Depends(get_current_user)):
    return get_prices(current_user.coins)


@app.get("/dashboard/news")
def dashboard_news(current_user: User = Depends(get_current_user)):
    return get_news(current_user.coins)


@app.get("/dashboard/meme")
def dashboard_meme(current_user: User = Depends(get_current_user)):
    # no argument — the meme isn't personalized, it's just random
    return get_meme()


@app.get("/dashboard/insight")
def dashboard_insight(current_user: User = Depends(get_current_user)):
    # defaults applied here, never stored — the frontend sends un-onboarded
    # users to the quiz, but that check runs in the browser and can be skipped
    coins = current_user.coins or ["BTC", "ETH"]
    investor_type = current_user.investor_type or "HODLer"
    return get_daily_insight(current_user.id, coins, investor_type)
