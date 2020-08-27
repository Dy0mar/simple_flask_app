# Flask with Docker

simple flask app with docker

## Tables

Users, Projects

## Usage

```bash
# top users who have the most projects
curl http://127.0.0.1:8000/api/v1.0/top/users

# projects (default page 1)
curl http://127.0.0.1:8000/api/v1.0/projects

# projects with pagination
curl http://127.0.0.1:8000/api/v1.0/projects/2

# projects with sort (sorted_date=ask/desc)
http://127.0.0.1:8000/api/v1.0/projects/2?sorted_date=desc

```