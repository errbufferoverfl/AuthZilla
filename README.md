<h1 align="center">AuthZilla</h1>
<div align="center">
</div>  
<div align="center">  
<strong>An experimental implementation of the OAuth 2.1 Authorisation Framework.</strong>  
</div>  
<div align="center">  
A small dopamine rabbit hole.  
</div>  

<br />  

<div align="center">  
<!-- Stability -->  
<!-- NPM version -->  
<!-- Build Status -->  
<!-- Test Coverage -->  
<!-- Downloads -->  
<!-- Standard -->  
</div>  

<div align="center">  
<h3>
<a href="https://example.com">Website</a>  
<span> | </span>  
<a href="https://github.com/AuthZilla">Handbook</a>  
<span> | </span>  
<a href="https://github.com/choojs/choo/blob/master/.github/CONTRIBUTING.md">Contributing</a>  
</h3>  
</div>  

<div align="center">  
<sub>The little experiment that could. Built with ❤︎ by  
<a href="https://twitter.com/errbufferoverfl">errbufferoverfl</a>
</div>  

## Introduction

AuthZilla is a minimal viable OAuth2.1 Authorisation server that experiments with how one can go about implementing the standards, best practices and informational RFCs. It isn't made for production deployment or use.

## Table of contents

- [Introduction](#introduction)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Migration Management](#migration-management)

## Tech Stack

Here's a brief high-level overview of the tech stack AuthZilla uses:

- The project is written in Python & uses the Flask micro web framework.
- For persistent storage (database), the app uses SQLite for local deployments.
- To send emails, the app can be configured to use a local SMTP mailer, or Mailgun.
- Secret hashing is handled by bcrypt.

## Getting Started

AuthZilla hasn't been built for real world deployment on the Internet.

Set your app's secret key as an environment variable. For example, add the following to your `.bashrc` or `.bash_profile`:

```shell  
export SECRET='something-really-secret'
```  

Before running shell commands, set `FLASK_APP` and `FLASK_DEBUG` environment variables:

```shell  
export FLASK_ENV=development
export FLASK_APP=corezilla.run
export FLASK_DEBUG=1
```  

Once the app is loaded various Flask utility functions can be accessed via the `flask` commend:

```bash
Commands:
  db       Perform database migrations.
  openapi  OpenAPI commands.
  roles    Role commands.
  routes   Show the routes for the app.
  run      Run a development server.
  shell    Run a shell in the app context.
  users    User commands.
```

## Migration Management

To run the development migrations make sure to set the following environment variables first:

```shell  
export FLASK_ENV=development
export FLASK_APP=corezilla.run
```  

### Running Migrations

1. Initialize Migrations Directory

If you haven't already initialized migrations, you need to set up a migrations folder. Run the following command in your project root:

```bash
flask db init
```

1. Create a Migration Script

After making changes to your models, you can create a new migration script by running:

```bash
flask db migrate -m "Your migration message"
```

1. Apply Migrations

To apply the migration to the database, run:

```bash
flask db upgrade
```

### Check the Migration Status

```bash
flask db current
```

### Delete All Migrations and Start Fresh

1. Delete the migrations Folder

Navigate to the project root and delete the entire migrations folder. This folder contains all the Alembic migration scripts.
You can do this manually by navigating to the project root and deleting the folder:

```bash
rm -rf migrations
```

1. Drop the Database Tables

You’ll need to drop all the existing database tables to make sure the database is clean before running new migrations.

Open a Python shell or use your Flask shell by running:

```bash
flask shell
```

Import your database instance and drop all tables:

```python
from corezilla.app import db
db.drop_all()
```

This will remove all the tables from the database, allowing you to start from scratch.

1. Recreate the migrations Folder

Once the old migrations are deleted and the tables are dropped, reinitialize the migrations folder using Flask-Migrate:

```bash
flask db init
```

This will create a fresh migrations folder with an empty migration history.

1. Generate a New Initial Migration

Now, generate a new migration based on the current state of your models:

```bash
flask db migrate -m "Initial migration"
```

This will create a new migration script in the migrations/versions folder that reflects the current state of your models.

1. Apply the Migration to the Database
Finally, apply the new migration to the database:

```bash
flask db upgrade
```

This will recreate your database tables based on the latest models.

# Common Problems

## How to Fix "Constraint must have a name" Error in Alembic Migrations

The "Constraint must have a name" error occurs when Alembic is managing database migrations, specifically when foreign keys, primary keys, or unique constraints are created or dropped without providing an explicit name. In SQLAlchemy, constraints should have names to ensure consistency across database migrations, especially during downgrades.

### 1. Understand the Problem

When Alembic auto-generates migrations, it might not always assign names to constraints (foreign keys, primary keys, etc.). While some databases like SQLite may allow unnamed constraints, others like Postgres or MySQL will require explicitly named constraints to manage schema changes.

You may encounter this error when:

- Creating or dropping foreign keys, unique constraints, or primary keys without a name.
- Performing migrations that rely on altering tables with constraints.

### 2. Fix the Issue: Add Explicit Constraint Names

#### 2.1 Identify the problematic operation

Look for operations in your Alembic migration files that create or drop constraints, such as:

```python
op.create_foreign_key()
op.drop_constraint()
op.create_primary_key()
op.create_unique_constraint()
```

For example, you may find lines like this:

```python
op.create_foreign_key(None, 'client', ['client_id'], ['id'])
```

Or:

```python
op.drop_constraint(None, 'client', type_='foreignkey')
```

These lines are missing explicit names for the constraints.

#### 2.2 Add explicit names

To fix the problem, you need to give each constraint a unique name. Update your migration script to provide a name for the constraint:

For foreign keys:

```python
op.create_foreign_key('fk_client_client_id', 'client', ['client_id'], ['id'])
```

For primary keys:

```python
op.create_primary_key('pk_client_owners', 'client_owners', ['user_id', 'client_id'])
```

For dropping constraints:

```python
op.drop_constraint('fk_client_user', 'client', type_='foreignkey')
```

Make sure to use descriptive and unique names that indicate the table and the columns involved in the constraint. This makes it easier to manage in the future.

### 3. Run the Migration

Once you have updated your migration script, rerun the migration:

``` bash
alembic upgrade head
```

If you made changes to fix the migration in a production database, always test on a staging environment first to verify that the constraints and migrations work as expected.

### 4. Preventing the Issue in the Future

#### 4.1 Use Explicit Names in Models

When defining your SQLAlchemy models, explicitly name your foreign keys and constraints in the models themselves to avoid the issue in future migrations. For example:

```python

class Client(db.Model):
__tablename__ = 'client'

id = db.Column(db.String(20), primary_key=True)
user_id = db.Column(db.String(), db.ForeignKey('user.id', name='fk_client_user_id'))
```

#### 4.2 Check Auto-generated Migrations

Before applying auto-generated migrations, review them for unnamed constraints and make necessary adjustments.