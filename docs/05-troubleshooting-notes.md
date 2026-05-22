## Module Import Troubleshooting

Issue:
- FastAPI container failed with:
  ModuleNotFoundError: No module named 'app.database'

Root Cause:
- database.py created in incorrect nested directory:
  services/asset_service/services/asset_service/app/

Resolution:
- moved database.py into:
  services/asset_service/app/
- removed accidental nested services directory
- rebuilt containers using:
  docker compose up -d --build

Key Lesson:
- Python module import paths depend on correct project structure alignment
- containerized application paths must match runtime import expectations