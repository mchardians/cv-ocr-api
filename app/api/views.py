from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OCRSerializers
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import re

# Create your views here.
class OCRView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OCRSerializers(data=request.data)

        if serializer.is_valid():
            cv = serializer.validated_data['cv']
            text = ""

            try:
                if cv.name.endswith('.pdf'):
                    cv_images = convert_from_bytes(cv.read(), 300)
                    
                    for page_num, image in enumerate(cv_images, start=1):
                        page_text = pytesseract.image_to_string(image)
                        text += f"== Halaman {page_num} ==\n{page_text}\n\n"
                else:
                    image = Image.open(cv)
                    text = pytesseract.image_to_string(image)
                
                structured_data = self.extract_data(text)

                return Response({
                    "data": structured_data
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def extract_data(self, text):
            name_match = re.search(r"\b([A-Za-z]+)( [A-Za-z]+)+\b", text)
            name = name_match.group(0) if name_match else None

            email_match = re.search(r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*", text)
            email = email_match.group(0) if email_match else None

            phone_match = re.search(r"(?:\+62|62|0)?[ -]?[]?\d{2,4}[]?[ -]?\d{3,4}[ -]?\d{3,4}[ -]?\d{0,5}", text)
            phone = phone_match.group(0) if phone_match else None

            summary_match = re.search(r"(?<=INTRODUCTION)(.*?)(?=EDUCATION|WORK EXPERIECE|SKILLS|FEATURED PROJECTS|CERTIFICATIONS|$)", text, re.S)
            summary = summary_match.group(0).strip() if summary_match else None

            education_matches = re.findall(r"(?P<institution>.+?)\n(?P<major>.+?)\n(?:Current GPA: (?P<gpa>\d\.\d{2}))?", text)
            
            # experience = re.findall(r"(\d{4}[-–]\d{4}).*?(?=\n|$)", text)
            
            structured_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "summary": summary,
                "educations": [
                    {
                    "institution": match[0].strip(),
                    "major": match[1].strip(),
                    "gpa": match[2] if match[2] else 0,
                    }
                    
                    for match in education_matches
                ],
                "experiences": [
                    None
                ],
                "skills": [
                    None
                ],
                "projects": [
                    None
                ],
                "certifications": [
                    None
                ]
            }

            return structured_data