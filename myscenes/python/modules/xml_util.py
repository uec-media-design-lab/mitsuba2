import sys 
import os 

def set_perspective(
        filepath, fov_axis="x", fov=39.6, focus_distance=1000, 
        origin=[0, 0, 100], target=[0, 0, 0], up=[0, 1, 0], 
        near_clip=0.01, far_clip=4000, spp=32):
    '''
    This function replace camera settings which described in xml file of mitsuba2 scene.
    NOTE:   
        - XML file can include only one sensor settings (including comment)

    @parameters
        - filepath (string) :          Full file path of xml file
        - fov_axis (string) :          Axis configuration of FOV
        - fov (float) :                Degree value of FOV
        - focus_distance (float)
        - origin, target, up (array) : Configuration of camera lookat
        - near_clip, far_clip :        View volume setting of camera
        - spp :                        The number of samples in rendering
    '''
    
    with open(filepath, mode="r", encoding="utf-8") as file:
        filelines = file.readlines()
    file.close()
    
    sensor_lines = [line_num for line_num, line in enumerate(filelines) if '<sensor type' in line or '</sensor>' in line]
    sensor_start = sensor_lines[0]  # Start line number of sensor setting
    sensor_end = sensor_lines[1]    # End line number of sensor setting
    for i, sensor_line in enumerate(filelines[sensor_lines[0]:sensor_lines[1]]):
        idx = i + sensor_start      # Index number of entire lines
        if sensor_line.find('fov_axis') > -1:
            toreplace = '\t\t<string name="fov_axis" value="{}"/>\n'.format(fov_axis)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('fov') > -1:
            toreplace = '\t\t<float name="fov" value="{}"/>\n'.format(fov)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)
        
        elif sensor_line.find('focus_distance') > -1:
            toreplace = '\t\t<float name="focus_distance" value="{}"/>\n'.format(focus_distance)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('origin') > -1:
            toreplace = '\t\t\t<lookat origin="{}, {}, {}"\n'.format(*origin)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('target') > -1:
            toreplace = '\t\t\t\t\ttarget="{}, {}, {}"\n'.format(*target)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('up') > -1:
            toreplace = '\t\t\t\t\tup="{}, {}, {}"/>\n'.format(*up)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('near_clip') > -1:
            toreplace = '\t\t<float name="near_clip" value="{}"/>\n'.format(near_clip)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)

        elif sensor_line.find('far_clip') > -1:
            toreplace = '\t\t<float name="far_clip" value="{}"/>\n'.format(far_clip)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)
        
        elif sensor_line.find('sample_count') > -1:
            toreplace = '\t\t\t<integer name="sample_count" value="{}"/>\n'.format(spp)
            filelines[idx] = filelines[idx].replace(filelines[idx], toreplace)
    
    with open(filepath, mode="w", encoding='utf-8') as f:
        f.writelines(filelines)
    f.close()

# For debugging
# xmlfilepath = 'xml/infloasion.xml'
# set_perspective(xmlfilepath)