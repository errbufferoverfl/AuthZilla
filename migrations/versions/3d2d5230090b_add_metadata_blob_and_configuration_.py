"""Add metadata_blob and configuration_blob fields to Client model with nested structures for URIs, CORS, refresh, and JWT settings.

Revision ID: 3d2d5230090b
Revises: 
Create Date: 2024-10-31 11:39:05.490704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d2d5230090b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.String(length=30), nullable=False),
    sa.Column('client_name', sa.String(length=255), nullable=True),
    sa.Column('_client_secret', sa.String(), nullable=True),
    sa.Column('client_uri', sa.String(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('app_type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_client_id'), ['client_id'], unique=True)

    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('fs_uniquifier', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=40), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('_password', sa.String(length=128), nullable=True),
    sa.Column('last_login_at', sa.String(), nullable=True),
    sa.Column('current_login_at', sa.String(), nullable=True),
    sa.Column('confirmed_at', sa.String(), nullable=True),
    sa.Column('last_login_ip', sa.String(length=255), nullable=True),
    sa.Column('current_login_ip', sa.String(length=255), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('fs_uniquifier'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fs_uniquifier'),
    sa.UniqueConstraint('username')
    )
    op.create_table('client_configuration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('configuration_blob', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client_configuration', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_configuration_id'), ['id'], unique=False)

    op.create_table('client_metadata',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('metadata_blob', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client_metadata', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_metadata_id'), ['id'], unique=False)

    op.create_table('client_owners',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.fs_uniquifier'], ),
    sa.PrimaryKeyConstraint('user_id', 'client_id')
    )
    op.create_table('roles_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.fs_uniquifier'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('installation_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('configuration_id', sa.String(), nullable=False),
    sa.Column('authorized_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['configuration_id'], ['client_configuration.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.fs_uniquifier'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('installation_record')
    op.drop_table('roles_users')
    op.drop_table('client_owners')
    with op.batch_alter_table('client_metadata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_metadata_id'))

    op.drop_table('client_metadata')
    with op.batch_alter_table('client_configuration', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_configuration_id'))

    op.drop_table('client_configuration')
    op.drop_table('user')
    op.drop_table('role')
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_client_id'))

    op.drop_table('client')
    # ### end Alembic commands ###
