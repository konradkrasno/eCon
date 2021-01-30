# eCon
![Alt text](./coverage.svg)

A platform to gather the construction site management aspects in one place.
It allows you to manage team tasks, communication between team members,
storage of documents, and calculation of the quantity survey of works.

### Dependencies
* Flask
* Sqlalchemy
* Celery
* Redis

### Design goals
- [x] Registering users and their authorization
- [x] Creating and managing projects
- [x] Creating workers and team
- [x] Creating a tool for quantity survey of masonry works
- [ ] Creating a custom page for quantity survey of works
- [x] Creating tasks for team members
- [ ] Creating chat for team members
- [x] Creating documents archiving

#### Example pages

Index page:

![index](https://user-images.githubusercontent.com/55924004/106360787-c9bf7780-631a-11eb-9985-73ab18dee188.png)

Team page:

![team](https://user-images.githubusercontent.com/55924004/106360790-caf0a480-631a-11eb-8d85-88110e43d1ed.PNG)

Tasks page:

![tasks](https://user-images.githubusercontent.com/55924004/106360973-b6f97280-631b-11eb-8b4f-12c616a6ad2c.png)

Documents page:

![documents](https://user-images.githubusercontent.com/55924004/106360786-c926e100-631a-11eb-8584-a126d3e60506.png)

Quantity survey of masonry works page:

![masonry_works](https://user-images.githubusercontent.com/55924004/106360933-78fc4e80-631b-11eb-9831-59d8775d1aa9.PNG)

### Running on development server
Clone the repository:
```bash
git clone https://github.com/konradkrasno/eCon.git
cd eCon
```
Create .env file:
```
SECRET_KEY=<your-secret-key>
MAIL_SERVER=<your-mail-server>
MAIL_PORT=<your-mail-port>
MAIL_USE_TLS=<1 or 0>
MAIL_USERNAME=<your-mail-username>
MAIL_PASSWORD=<you-mail-password>
MAIL_DEFAULT_SENDER=<default-sender>

# Default postgres db
DATABASE_URL=postgresql+psycopg2://postgres:password@postgres:5432
```
Start docker containers:
```bash
docker-compose up -d
```
Run tests:
```bash
docker exec -it web bash
pytest
```
