'''
fastapi의 시작점
-> api3.py파일에서 Connect3 클래스를 참조하여 사용!
'''
from api import Api
# import uvicorn
run = Api()
app = run.app


# if __name__ == "__main__":
#      uvicorn.run(app, host="10.101.64.46", port=8000)