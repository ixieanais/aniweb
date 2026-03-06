from sqlalchemy import String, Integer, Text, Boolean, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReleasesOrm(Base):
    __tablename__ = "releases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    english_name: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    poster: Mapped[str | None] = mapped_column(String(255))
    alias: Mapped[str | None] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    age_rating: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[str | None] = mapped_column(Text)
    is_ongoing: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int | None] = mapped_column(BigInteger)
    updated_at: Mapped[int | None] = mapped_column(BigInteger)
    fresh_at: Mapped[int | None] = mapped_column(BigInteger)
    total_episodes: Mapped[int | None] = mapped_column(Integer)


class EpisodesOrm(Base):
    __tablename__ = "episodes"

    __table_args__ = (
        UniqueConstraint("release_id", "ordinal"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    anime_name: Mapped[str | None] = mapped_column(String(255))
    episode_name: Mapped[str | None] = mapped_column(String(255))
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    opening: Mapped[str | None] = mapped_column(String(255))
    ending: Mapped[str | None] = mapped_column(String(255))
    duration: Mapped[int | None] = mapped_column(Integer)
    preview: Mapped[str | None] = mapped_column(String(255))
    url_1080: Mapped[str | None] = mapped_column(String(255))
    url_720: Mapped[str | None] = mapped_column(String(255))
    url_480: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(Text, nullable=False)

    release_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("releases.id", ondelete="CASCADE"),
        nullable=False
    )


class UsersOrm(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    connected_at: Mapped[int | None] = mapped_column(BigInteger)
    last_visit_at: Mapped[int | None] = mapped_column(BigInteger)


class FavoritesOrm(Base):
    __tablename__ = "favorites"

    uid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uid", ondelete="CASCADE"),
        primary_key=True
    )
    release_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("releases.id", ondelete="CASCADE"),
        primary_key=True
    )
    added_at: Mapped[int | None] = mapped_column(BigInteger)


class ViewedOrm(Base):
    __tablename__ = "viewed"

    uid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uid", ondelete="CASCADE"),
        primary_key=True
    )
    episode_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("episodes.id", ondelete="CASCADE"),
        primary_key=True
    )
    release_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("releases.id", ondelete="CASCADE"),
        nullable=False
    )
    added_at: Mapped[int | None] = mapped_column(BigInteger)


class ViewTimeOrm(Base):
    __tablename__ = "view_time"

    uid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uid", ondelete="CASCADE"),
        primary_key=True
    )
    release_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("releases.id", ondelete="CASCADE"),
        primary_key=True
    )
    episode_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=False
    )
    time: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[int | None] = mapped_column(BigInteger)


class ExpiresInOrm(Base):
    __tablename__ = "expires_in"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    expires_in: Mapped[int] = mapped_column(Integer, nullable=False)