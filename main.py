from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import swisseph as swe
import datetime

app = FastAPI(title="Kundli Generator API")

# Enable CORS (So your frontend can communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Active", "message": "Kundli API Running Successfully!"}

# 🛠️ NAYA ADD KIYA: kundli.html file ko serve karne ke liye routes
@app.get("/kundli.html")
@app.get("/kundli")
def serve_kundli():
    return FileResponse("kundli.html")

@app.post("/calculate-kundli")
def calculate_kundli(
    name: str = Form(...),
    dob: str = Form(...),    # Format: YYYY-MM-DD
    time: str = Form(...),   # Format: HH:MM
    lat: float = Form(...),  # Latitude (e.g., 23.0225 for Ahmedabad)
    lon: float = Form(...)   # Longitude (e.g., 72.5714 for Ahmedabad)
):
    try:
        # Date & Time parse karna
        y, m, d = map(int, dob.split('-'))
        hh, mm = map(int, time.split(':'))
        
        # Julian Day calculate karna (Swiss Ephemeris ke liye)
        decimal_time = hh + (mm / 60.0)
        julian_day = swe.julday(y, m, d, decimal_time)
        
        # Main Planetary Positions Calculate karna
        planets = {
            "Sun": swe.calc_ut(julian_day, swe.SUN)[0][0],
            "Moon": swe.calc_ut(julian_day, swe.MOON)[0][0],
            "Mars": swe.calc_ut(julian_day, swe.MARS)[0][0],
            "Mercury": swe.calc_ut(julian_day, swe.MERCURY)[0][0],
            "Jupiter": swe.calc_ut(julian_day, swe.JUPITER)[0][0],
            "Venus": swe.calc_ut(julian_day, swe.VENUS)[0][0],
            "Saturn": swe.calc_ut(julian_day, swe.SATURN)[0][0],
            "Rahu": swe.calc_ut(julian_day, swe.MEAN_NODE)[0][0],
        }
        
        # Planetary degree se Rashi (Sign) nikalna
        zodiac_signs = [
            "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
            "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
            "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
        ]
        
        result = {}
        for planet, degree in planets.items():
            sign_index = int(degree // 30)
            sign_degree = round(degree % 30, 2)
            result[planet] = {
                "sign": zodiac_signs[sign_index],
                "degree": sign_degree
            }

        return {
            "success": True,
            "user_details": {"name": name, "dob": dob, "time": time},
            "planetary_positions": result
        }

    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})
