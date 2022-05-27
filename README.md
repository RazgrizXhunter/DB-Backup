# DB-Backup

DB-Backup is a script designed to backup projects with their respective databases automatically and upload backup files to AWS' S3 with Boto3. It also includes Sendgrid to notify people responsible for the backups in case something goes wrong and the backup couldn't be done.

## Conception

The project was conceived to automatize Databases backup for Innovaweb's S&O Area as part of the creation of a suite of tools to manage the client's projects. There's a plan for it to be integrated into the [Support Management](https://github.com/innovawebcl/support-management) tool to provide notifications shown in the dashboard about backups health.