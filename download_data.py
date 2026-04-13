from roboflow import Roboflow
rf = Roboflow(api_key="LMgGPC9NivZoNzaHEtbl")
project = rf.workspace("s-workspace-rfpbj").project("korea-car-plat-bubuv")
version = project.version(1)
dataset = version.download("yolov8")
                