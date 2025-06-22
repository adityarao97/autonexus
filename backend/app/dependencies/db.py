def get_db():
    # Mock DB connection (replace with real one)
    db = {}
    try:
        yield db
    finally:
        pass  # Close DB if needed
