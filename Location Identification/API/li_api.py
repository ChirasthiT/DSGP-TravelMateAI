from fastapi import FastAPI, File, HTTPException, UploadFile
from image_indentification import Image_Identification


app = FastAPI()
image_indentification = Image_Identification()

@app.post("/image_predict/")
async def image_predict(file: UploadFile = File(...)):
    try:
        # Read the uploaded image file
        image_bytes = await file.read()

        # Perform prediction
        prediction = image_indentification.predict(image_bytes)

        return prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "An error occurred during prediction", "details": str(e)}
        )
    
# uvicorn main:app --reload --port 8600