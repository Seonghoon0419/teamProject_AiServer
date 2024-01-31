import bpy
import bmesh
import os
import sys


blender_onefloor_path = os.path.abspath("C:/Users/wjdtj/OneDrive/바탕 화면/teamProject_AiServer/teamProject_AiServer/blender_file/building_1.blend")
blender_file_path = os.path.abspath("C:/Users/wjdtj/OneDrive/바탕 화면/teamProject_AiServer/teamProject_AiServer/blender_file/building_2.blend")

#블랜더 건물 층별 객체 확인목적
#output_blend_path = os.path.abspath("C:/teamProject_AiServer/blender_file/blederTest.blend")

def buildBuilding(count, output_gltf_path):
    if (count == 1):
       building_name = "floor.001"
       count = 0
       bpy.ops.wm.open_mainfile(filepath=blender_onefloor_path)
    else:
        #건물 객체 선택
        building_name = "building.001"
        bpy.ops.wm.open_mainfile(filepath=blender_file_path)

    building = bpy.data.objects[building_name]
    bpy.context.view_layer.objects.active = building
    building.select_set(True)
    # 배열 모디파이어 추가 및 설정
    if "Array" not in building.modifiers:
        building_modifier = building.modifiers.new(name="Array", type='ARRAY')
    else:
        building_modifier = building.modifiers["Array"]


    floor = bpy.data.objects["floor.001"]
    bpy.context.view_layer.objects.active = floor


    # 배열 모디파이어 설정
    building_modifier.relative_offset_displace[0] = 0  # X축 방향 비활성화
    building_modifier.relative_offset_displace[1] = 0  # Y축 방향 비활성화
    building_modifier.relative_offset_displace[2] = 1  # Z축 방향 활성화 (위로 복제)
    building_modifier.count = count-1 # 층수 설정

    floor.select_set(True)
    if floor.modifiers.get("Array"):
        # Array Modifier 적용
        bpy.ops.object.modifier_apply(modifier="Array")
    else:
        print(f"No Array Modifier found on '{building_name}' object.")

    # 에딧 모드로 전환
    bpy.ops.object.mode_set(mode='EDIT')

    # 메쉬 세퍼레이트(Separate) - 루스 파트(Loose Parts)로 분리
    bpy.ops.mesh.separate(type='LOOSE')

    # 오브젝트 모드로 돌아오기
    bpy.ops.object.mode_set(mode='OBJECT')

    for index, obj in enumerate(bpy.context.selected_objects, start=1):
        obj.name = f"{index}"


    #bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)
    # GLTF 파일 저장
    building_path = bpy.ops.export_scene.gltf(filepath=output_gltf_path, export_format='GLB', use_selection=True)
    #test = os.path.abspath("C:/teamProject_AiServer/blender_file/test.glb")
    #bpy.ops.export_scene.gltf(filepath=test, export_format='GLB', use_selection=True)

    return building_path


if __name__ == "__main__":
    if len(sys.argv) < 4:  # JSON 데이터와 GLTF 파일 경로
        print("Not enough arguments provided.")
        sys.exit(1)
    count = int(sys.argv[-2])
    output_gltf_path = sys.argv[-1]  # GLTF 파일 경로
    buildBuilding(count, output_gltf_path)


