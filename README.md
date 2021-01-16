# eCon
A platform to gather the construction site management aspects in one place.
It allows you to manage team tasks, communication between team members,
storage of documents, and calculation of the quantity survey of works.

### Design goals
- [x] Registering users and their authorization
- [x] Creating and managing projects
- [x] Creating workers and team
- [x] Creating a tool for quantity survey of masonry works
- [ ] Creating a custom page for quantity survey of works
- [x] Creating tasks for team members
- [ ] Creating chat for team members
- [ ] Creating documents archiving

#### Example pages

Investments page:

![investments](https://user-images.githubusercontent.com/55924004/103815285-69168500-5063-11eb-83e2-5056920c8893.PNG)

Team page:

![team](https://user-images.githubusercontent.com/55924004/103815534-c9a5c200-5063-11eb-9a92-32946cbded2a.PNG)

Quantity survey of masonry works page:

![masonry_works](https://user-images.githubusercontent.com/55924004/103815332-83506300-5063-11eb-8484-ccba8c7d794a.PNG)

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
