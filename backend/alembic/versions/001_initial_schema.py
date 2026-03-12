"""Initial schema with PostgreSQL ENUMs and UUID v7.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-02-17 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PostgreSQL ENUM types
    videostatus_enum = ENUM(
        'QUEUED', 'SCRIPTING', 'SCRIPT_VALIDATED', 'IMAGE_GENERATION',
        'VOICE_SYNTHESIS', 'MEDIA_COMPOSITION', 'ENCODING', 'UPLOADING',
        'DONE', 'FAILED',
        name='videostatus',
        create_type=False
    )
    
    platform_enum = ENUM(
        'TIKTOK', 'REELS', 'SHORTS',
        name='platform',
        create_type=False
    )
    
    userplan_enum = ENUM(
        'FREE', 'PRO', 'ENTERPRISE',
        name='userplan',
        create_type=False
    )
    
    assettype_enum = ENUM(
        'IMAGE', 'AUDIO',
        name='assettype',
        create_type=False
    )
    
    # Create ENUMs in database
    videostatus_enum.create(op.get_bind(), checkfirst=True)
    platform_enum.create(op.get_bind(), checkfirst=True)
    userplan_enum.create(op.get_bind(), checkfirst=True)
    assettype_enum.create(op.get_bind(), checkfirst=True)
    
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('plan', userplan_enum, nullable=False, server_default='FREE'),
        sa.Column('minutes_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_user_email', 'user', ['email'])
    
    # Create template table
    op.create_table(
        'template',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('platform', platform_enum, nullable=False),
        sa.Column('style_config', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        # Legacy fields for backward compatibility
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('structure_json', sa.String(), nullable=True),
    )
    
    # Create video table
    op.create_table(
        'video',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('platform', platform_enum, nullable=False),
        sa.Column('status', videostatus_enum, nullable=False, server_default='QUEUED'),
        sa.Column('storage_key', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_step', videostatus_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        # Legacy fields for backward compatibility
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['template.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_video_user_id', 'video', ['user_id'])
    op.create_index('ix_video_status', 'video', ['status'])
    op.create_index('ix_video_created_at', 'video', ['created_at'])
    
    # Create videojob table
    op.create_table(
        'videojob',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('video_id', UUID(as_uuid=True), nullable=False),
        sa.Column('step', videostatus_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_videojob_video_id', 'videojob', ['video_id'])
    
    # Create asset table
    op.create_table(
        'asset',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('video_id', UUID(as_uuid=True), nullable=False),
        sa.Column('type', assettype_enum, nullable=False),
        sa.Column('storage_key', sa.String(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_asset_video_id', 'asset', ['video_id'])
    
    # Create trigger for updated_at auto-update on user table
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON "user"
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_video_updated_at BEFORE UPDATE ON video
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_video_updated_at ON video')
    op.execute('DROP TRIGGER IF EXISTS update_user_updated_at ON "user"')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # Drop tables
    op.drop_index('ix_asset_video_id', 'asset')
    op.drop_table('asset')
    
    op.drop_index('ix_videojob_video_id', 'videojob')
    op.drop_table('videojob')
    
    op.drop_index('ix_video_created_at', 'video')
    op.drop_index('ix_video_status', 'video')
    op.drop_index('ix_video_user_id', 'video')
    op.drop_table('video')
    
    op.drop_table('template')
    
    op.drop_index('ix_user_email', 'user')
    op.drop_table('user')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS assettype')
    op.execute('DROP TYPE IF EXISTS userplan')
    op.execute('DROP TYPE IF EXISTS platform')
    op.execute('DROP TYPE IF EXISTS videostatus')
