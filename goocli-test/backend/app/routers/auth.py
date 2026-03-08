from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from app import schemas, models
from app.database import get_db
from app.utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, upload_to_s3
from app.models.models import User

# router will enable this script to be used as decoratives in main
router = APIRouter()
# token (proverbial cookie) created for each user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Given a token (Proverbial cookie) and the db
    if token correspond to a user, it will return a JSON with user data
    Another case it will raise a customized credentials_exception
    """
    # Pre set a customized error "credentials_exception" in case something went wrong
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode the code using algorithm .env declared
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # sub is the key associated with the value (email)
        # If no email, token incorrect and return credentials_exception
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email) # Create a TokenData Object, defined in schemas.py
    except JWTError:
        # If can't decode the token, then we assume a Credentials_exception
        raise credentials_exception
    # Search for user using the known info and the now verified email
    user = db.query(User).filter(User.email == token_data.email).first()
    # If user doesn't exist in db, credentials_excpetion
    if user is None:
        raise credentials_exception
    # If reach until here, then return a JSON with user info
    return user

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Given an user of type usercreate(defined in schemas) and the db of actual sessionS
    If no errors, database will be updated with new user info
    """
    # Check if user(email) already in database. If so then we raise an exception
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Return a hashed password in VSCode you can put your cursor in function name and it will return
    # a summarize of the function, defined in utils
    hashed_password = get_password_hash(user.password)
    # Using User class(defined in models.py) will create a new object appt to be added a DB
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        age=user.age
    )
    # Add new user, confirm, and assign a ID to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Given the login info, and the db
    If nothin went wrong it will return an object with the token (proverbial cookie) of that login and the type of the token will be bearer
    JSON example : {"access_token": access_token, "token_type": "bearer"}
    """
    # user will be a object(table) result of the search in database of login info
    user = db.query(User).filter(User.email == form_data.username).first()
    # If user doesn't exist() in database or if password is incorrect, we raise an exception
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # If all is correct, we create an access token, with sub being a key for email value
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/upload-profile-image", response_model=schemas.UserResponse)
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Give a File, and automaticaly collect the current_user and db
    If nothing went wrong, it will return the current_user
    """
    url = upload_to_s3(file.file, file.filename, folder=f"profiles/{current_user.id}")
    # If upload_to_s3 return None, failed to upload image and raise exception
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
    # Update info of current user and commit that info to database
    current_user.profile_image_url = url
    db.commit()
    db.refresh(current_user)
    # Return the new current_user
    return current_user

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Just return current_user
    """
    return current_user
