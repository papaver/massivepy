#------------------------------------------------------------------------------
# mas_blocks.py - Blocks found in Massive scene files. (.mas)
#------------------------------------------------------------------------------

import os
import re

from scanf import sscanf
from scanf import IncompleteCaptureError

from block  import Block
from common import Variable

#------------------------------------------------------------------------------
# class DisplayOptionsBlock
#------------------------------------------------------------------------------

class DisplayOptionsBlock(Block):
    """User interface display options.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "shade %d",
        "shadows %d",
        "shadow_bias %g",
        "shadow_colour %g %g %g",
        "shadow_map_resolution %d",
        "backfaces %d",
        "blocky %d",                    # never parsed?
        "cameras %d",
        "lanes %d",
        "lights %d",
        "filmback %d",
        "crop_filmback %d",
        "masks %d",
        "heads_up %d",
        "grid %d %f %f",
        "motion_blur %d %d %f",
        "antialias %d",
        "standins %d",
        "sprites %d",
        "statistics %d",
        "time %d",
        "time_in_frames %d",
        "vision %d %d",
        "sound_emission %d",
        "sound_reception %d",
        "sound_rules %d",
        "links %d",
        "connected %d",
        "material_links %d",
        "cloth_active %d",
        "hair_active %d",
        "terrain %d",
        "shade_terrain %d",
        "terrain_lines %d",
        "terrain_map %d",
        "terrain_alpha %d",
        "terrain_toggle %s",
        "subdiv_quality %d %f",
        "subdivs %d",
        "agent_fields %d",
        "playbacks %d",                 # always written out as 1?
        "triggers %d",                  # always written out as 1?
        "wind_display_scale %g",
        "handle_scale %g",
        "render_pass %s",
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(DisplayOptionsBlock, self).__init__()
        special_list = { "terrain_toggle" : self._parseAttributeString }
        self.parseAttributes(
            block, DisplayOptionsBlock._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self.printAttributes(DisplayOptionsBlock._sBlockFormatting)
        return "Display options\n%sEnd display options" % self._addIndent(block)

#------------------------------------------------------------------------------
# class TerrainsBlock
#------------------------------------------------------------------------------

class TerrainsBlock(Block):
    """Scene terrains.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "texture_process %d",
        "texture_process_width %d",
        "texture_process_multiply %g",
        "texture_process_skip %d",
        "texture_process_paint_planes %d",
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(TerrainsBlock, self).__init__()
        self.terrains = []
        special_list = { "terrain" : self._parseTerrain }
        self.parseAttributes(block, TerrainsBlock._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        terrains   = "".join(map(str, self.terrains))
        attributes = self.printAttributes(TerrainsBlock._sBlockFormatting)
        block      = "%s%s" % (terrains, attributes)
        return "Terrains\n%sEnd terrains" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseTerrain(self, block):
        """Collate all of the terrains in the scene.
        """
        self.terrains.append(TerrainNode(block))

#------------------------------------------------------------------------------
# class TerrainNode
#------------------------------------------------------------------------------

class TerrainNode(Block):
    """Terrain in the scene.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "translate %d %d",
        "model %s",
        "texmap %s",
        "display",
        "active",
        "dynamic",
        "flip_normals",
        "visible_to_agents",
        "render_pass %s",
        "ambient %g %g %g %s",
        "diffuse %g %g %g %s",
        "specular %g %g %g %s",
        "roughness %g",
        "shader %s",
        "displacement %s",
        "displ_bounds %s",
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(TerrainNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # setup special parse list
        special_list = {
            "render_pass"  : self._parseAttributeString,
            "shader"       : self._parseAttributeString,
            "displacement" : self._parseAttributeString,
            "displ_bounds" : self._parseAttributeString
        }

        # parse the attributes
        self.parseAttributes(block, TerrainNode._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "terrain %s" % self.name
        block  = self.printAttributes(TerrainNode._sBlockFormatting)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Terrain block header contains terrain name.
        """
        formating    = "terrain %s"
        (self.name,) = sscanf(header, formating)

#------------------------------------------------------------------------------
# class CamerasBlock
#------------------------------------------------------------------------------

class CamerasBlock(Block):
    """Scene cameras and camera clipping planes.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "clipping_planes %d",
        "clipping_plane %d [%g %g %g %g]",
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(CamerasBlock, self).__init__()
        self.cameras = []
        special_list = { "camera" : self._parseCamera }
        self.parseAttributes(block, CamerasBlock._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        cameras    = "".join(map(str, self.cameras))
        attributes = self.printAttributes(CamerasBlock._sBlockFormatting)
        block      = "%s%s" % (cameras, attributes)
        return "Cameras\n%sEnd cameras" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseCamera(self, block):
        """Collate all of the cameras in the scene.
        """
        self.cameras.append(CameraNode(block))

#------------------------------------------------------------------------------
# class CameraNode
#------------------------------------------------------------------------------

class CameraNode(Block):
    """Camera in the scene.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "translate %d %d",      # parse manually
        "fov %g",
        "filmback %g %g",
        "zrange   %g %g",
        "pixel_aspect %g",
        "bgpic %s %d",
        "order %s",             # not sure what this is
        "keyable %s",           # cx, cy, cz, tx, ty, tz, rx, ry, rz
        "file %s",
        "frame_offset %d",
        "translate %g %g %g",
        "rotate %g %g %g",
        "pivot %g %g %g",
        "display_fustrum",
        "constrain %s",         # follow_xz | follow_3d | lookat | pov | agent
        "constrain %s %s",
        "filter %d %f",
        "volume \"%s\" %s %s",
        "lens \"%s\" %s %s",
    ]

    #--------------------------------------------------------------------------
    # enums
    #--------------------------------------------------------------------------

    class kConstrain:
        LookAt   = 'lookat'
        Agent    = 'agent'
        Pov      = 'pov'
        FollowXZ = 'follow_xy'
        Follow3D = 'follow_3d'

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(CameraNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # first line contains node position for the ui, needs to be parsed
        #  seperately since the 'translate' tag is used twice
        line, block = block.partition('\n')[::2]
        self.position = sscanf(line, CameraNode._sBlockFormatting[0])

        # setup special parse list
        special_list = {
            "keyable" : self._parseAttributeString
        }

        # parse the rest of the attributes
        self.parseAttributes(
            block, CameraNode._sBlockFormatting[1:], special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        header     = ("camera %s *" if self.selected else "camera %s") % self.name
        position   = CameraNode._sBlockFormatting[0] % self.position
        attributes = self.printAttributes(CameraNode._sBlockFormatting[1:])
        block      = "%s\n%s" % (position, attributes)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Camera block header contains camera name and selection status.
        """

        normal   = "camera %s"
        selected = "camera %s *"

        # check if camera selected
        try:
            (self.name,)  = sscanf(header, selected)
            self.selected = True
        except IncompleteCaptureError, e:
            (self.name,)  = sscanf(header, normal)
            self.selected = False

#------------------------------------------------------------------------------
# class LightingBlock
#------------------------------------------------------------------------------

class LightingBlock(Block):
    """Scene lights.
    """

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(LightingBlock, self).__init__()
        self.lights  = []
        special_list = { "light" : self._parseLight }
        self.parseAttributes(block, [], special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = "".join(map(str, self.lights))
        return "Lighting\n%sEnd lighting" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseLight(self, block):
        """Collate all of the lights in the scene.
        """
        self.lights.append(LightNode(block))

#------------------------------------------------------------------------------
# class LightNode
#------------------------------------------------------------------------------

class LightNode(Block):
    """Light in the scene.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    # [moiz] skipping most of the attributes here, mostly useless and high
    #   complexity with very minimum reward

    _sBlockFormatting = [
       "translate %d %d",
       "colour   %g %g %g",
       "intensity %g",
       "type %s"           # ambient, directional, point, spot
    ]

    #--------------------------------------------------------------------------
    # enums
    #--------------------------------------------------------------------------

    class kType:
        Ambient     = 'ambient'
        Directional = 'directional'
        Point       = 'point'
        Spot        = 'spot'

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(LightNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # first line contains node position for the ui, needs to be parsed
        #  seperately since the 'translate' tag is used twice
        line, block = block.partition('\n')[::2]
        self.position = sscanf(line, LightNode._sBlockFormatting[0])

        # parse the rest of the attributes
        rest = self.parseAttributes(block, LightNode._sBlockFormatting[1:])

        # save remaining attributes
        self._raw = rest

    #--------------------------------------------------------------------------

    def __str__(self):
        header     = "light %s" % self.name
        position   = LightNode._sBlockFormatting[0] % self.position
        attributes = self.printAttributes(LightNode._sBlockFormatting[1:])
        block      = "%s\n%s%s" % (position, attributes, self._raw)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Light block header contains light name.
        """
        formating    = "light %s"
        (self.name,) = sscanf(header, formating)

#------------------------------------------------------------------------------
# class RendersBlock
#------------------------------------------------------------------------------

class RendersBlock(Block):
    """Render options.
    """

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(RendersBlock, self).__init__()
        self.renders = []
        special_list = { "render" : self._parseRender }
        self.parseAttributes(block, [], special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = "".join(map(str, self.renders))
        return "Renders\n\n%sEnd renders" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseRender(self, block):
        """Collate all of the render enties for the scene.
        """
        self.renders.append(RenderOption(block))

#------------------------------------------------------------------------------
# class RenderOption
#------------------------------------------------------------------------------

class RenderOption(Block):
    """Render option settings.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    # [moiz] skipping most of the attributes here, mostly useless and high
    #   complexity with very minimum reward

    _sBlockFormatting = [
        "images %s",
        "render_files %s",
        "render_pass_name %s",
        "camera %s",
        "renderer %i",            # prman=1, air=2, 3delight=3, velocity=4, mentalray=5, vary=6
        "resolution_option %i",
        "resolution %i %i",
        "pixel_samples %i %i",
        "auto_light %s",
        "auto_render_pass %s %s",
        "shadows %i",
        "mblur %i"
    ]

    #--------------------------------------------------------------------------
    # enums
    #--------------------------------------------------------------------------

    class kRenderer:
        PRMan        = 1
        Air          = 2
        ThreeDelight = 3
        Velocity     = 4
        MentalRay    = 5
        VRay         = 6

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(RenderOption, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # parse the attributes
        rest = self.parseAttributes(block, RenderOption._sBlockFormatting)

        # save remaining attributes
        self._raw = rest

    #--------------------------------------------------------------------------

    def __str__(self):
        header      = ("render %s *" if self.selected else "render %s") % self.name
        attributes  = self.printAttributes(RenderOption._sBlockFormatting)
        block      = "%s%s" % (attributes, self._raw)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Render options block header contains render name and selection status.
        """

        normal   = "render %s"
        selected = "render %s *"

        # check if render selected
        try:
            (self.name,)  = sscanf(header, selected)
            self.selected = True
        except IncompleteCaptureError, e:
            (self.name,)  = sscanf(header, normal)
            self.selected = False

#------------------------------------------------------------------------------
# class DynamicsBlock
#------------------------------------------------------------------------------

class DynamicsBlock(Block):
    """Represent the dynamics settings.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "terrain_collisions %d",
        "self_collisions %d",
        "object_collisions %d",
        "rotation_constraints %d",
        "spring_forces %d",
        "spring_collisions %d",
        "drag_forces %d",
        "quickstep %d",
        "rbd_solver %s"            # ode, glowworm
    ]

    #--------------------------------------------------------------------------
    # enums
    #--------------------------------------------------------------------------

    class kSolver:
        Ode      = 'ode'
        GlowWorm = 'glowworm'

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(DynamicsBlock, self).__init__()
        self.parseAttributes(block, DynamicsBlock._sBlockFormatting)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self.printAttributes(DynamicsBlock._sBlockFormatting)
        return "Dynamics\n%sEnd dynamics" % self._addIndent(block)

#------------------------------------------------------------------------------
# class FlowBlock
#------------------------------------------------------------------------------

class FlowBlock(Block):
    """Scene flow fields.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "indicators %d x %d",
        "gap [%g %g %g] %g %g"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(FlowBlock, self).__init__()

        # initialize fields
        self.splines = []
        self.gaps    = []

        # setup special parse list
        special_list = { "spline" : self._parseSpline }

        # parse the attributes
        self.parseAttributes(block, FlowBlock._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        attributes = self.printAttributes(FlowBlock._sBlockFormatting[:1])
        splines    = "\n".join(map(str, self.splines))
        gaps       = self._printGaps() if self.gap else ""
        block      = "%s%s\n%s" % (attributes, splines, gaps)
        return "Flow\n%sEnd flow" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseSpline(self, block):
        """Collate all of the flow field splines.
        """
        self.splines.append(FlowSpline(block))

    #--------------------------------------------------------------------------

    def _printGaps(self):
        formatting = FlowBlock._sBlockFormatting[1]
        gaps       = [self.gap] if not isinstance(self.gap, list) else self.gap
        return "\n".join([formatting % gap for gap in gaps]) + "\n"

#------------------------------------------------------------------------------
# class FlowSpline
#------------------------------------------------------------------------------

class FlowSpline(Block):
    """Spline used to represent a flow field.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sSplineFormatting = "spline %g %g %g %g %d"

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(FlowSpline, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # parse the points
        self._parsePoints(block)

    #--------------------------------------------------------------------------

    def __str__(self):
        header = FlowSpline._sSplineFormatting % self.spline
        block  = self._printPoints()
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Spline block header contains unknown data and number of points.
        """
        formatting  = FlowSpline._sSplineFormatting.replace('%g', '%f')
        self.spline = sscanf(header, formatting)

    #--------------------------------------------------------------------------

    def _parsePoints(self, block):
        """Points representing spline. 
        """
        self.points = []
        for line in block.strip('\n').split('\n'):
            point = sscanf(line, "[%f %f %f %f %f %f %f %f %f %f]")
            self.points.append(point)

    #--------------------------------------------------------------------------

    def _printPoints(self):
        formatting = "[%g %g %g %g %g %g %g %g %g %g]"
        points     = "\n".join([formatting % point for point in self.points])
        return points

#------------------------------------------------------------------------------
# class LaneBlock
#------------------------------------------------------------------------------

class LaneBlock(Block):
    """Scene lanes.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "spline %d %g %g"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(LaneBlock, self).__init__()
        self.splines = []
        special_list = { "spline" : self._parseSpline }
        self.parseAttributes(block, [], special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = "".join(map(str, self.splines))
        return "Lane\n%sEnd lane" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseSpline(self, block):
        """Collate all of the flow field splines.
        """
        self.splines.append(LaneSpline(block))

#------------------------------------------------------------------------------
# class LaneSpline
#------------------------------------------------------------------------------

class LaneSpline(Block):
    """Spline used to represent a lane.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sSplineFormatting = "spline %d %g %g"

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(LaneSpline, self).__init__()

        # initialize fields
        self.points   = []
        self.tangents = None

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # parse the points
        rest = self._parsePoints(block, self.count)

        # parse tangents
        self.tangents = None
        if rest.startswith("tangents"):
            self._parseTangents(rest)

    #--------------------------------------------------------------------------

    def __str__(self):
        header   = LaneSpline._sSplineFormatting % (self.count, self.hue, self.width)
        points   = self._printPoints()
        tangents = self._printTangents() if self.tangents else ""
        block    = "%s\n%s" % (points, tangents)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Spline block header contains point count, hue, and width.
        """
        formatting  = LaneSpline._sSplineFormatting.replace('%g', '%f')
        (self.count, self.hue, self.width) = sscanf(header, formatting)

    #--------------------------------------------------------------------------

    def _parsePoints(self, block, count):
        """Points representing spline. 
        """
        lines = block.strip('\n').split('\n')
        for line in lines[:count]:
            point = sscanf(line, "[%f %f %f %f]")
            self.points.append(point)
        return "\n".join(lines[count:])

    #--------------------------------------------------------------------------

    def _printPoints(self):
        formatting = "[%g %g %g %g]"
        points     = "\n".join([formatting % point for point in self.points])
        return points

    #--------------------------------------------------------------------------

    def _parseTangents(self, block):
        """Tangents representing spline. 
        """
        self.tangents = []
        for line in block.strip('\n').split('\n')[1:]:
            tangent = sscanf(line, "[%f %f %f][%f %f %f]")
            self.tangents.append(tangent)

    #--------------------------------------------------------------------------

    def _printTangents(self):
        formatting = "[%g %g %g][%g %g %g]"
        tangents   = "\n".join([formatting % tangent for tangent in self.tangents])
        return "tangents\n%s\n" % tangents

#------------------------------------------------------------------------------
# class SimsBlock
#------------------------------------------------------------------------------

class SimsBlock(Block):
    """Simulation options.
    """

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(SimsBlock, self).__init__()
        self.sims    = []
        special_list = { "sim" : self._parseSim }
        self.parseAttributes(block, [], special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = "".join(map(str, self.sims))
        return "Sims\n%sEnd sims" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseSim(self, block):
        """Collate all of the sim enties for the scene.
        """
        self.sims.append(SimOption(block))

#------------------------------------------------------------------------------
# class SimOption
#------------------------------------------------------------------------------

class SimOption(Block):
    """Simulation option settings.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "frames %d %d %d"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(SimOption, self).__init__()

        # initialize fields
        self.process = None
        self.input   = None
        self.output  = None

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # setup special parse list
        special_list = {
            "process" : self._parseProcess,
            "input"   : self._parseInput,
            "output"  : self._parseOutput
        }

        # setup skip list
        skip_list = ['end']

        # parse the attributes
        self.parseAttributes(
            block, SimOption._sBlockFormatting, special_list, skip_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        header     = ("sim %s *" if self.selected else "sim %s") % self.name
        attributes = self.printAttributes(SimOption._sBlockFormatting)
        process    = str(self.process) if self.process else ""
        input      = str(self.input) if self.input else ""
        output     = str(self.output) if self.output else ""
        block      = "%s%s%s%s" % (attributes, process, input, output)
        return "%s\n%send sim\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Sim block header contains sim name and selection status.
        """

        normal   = "sim %s"
        selected = "sim %s *"

        # check if camera selected
        try:
            (self.name,)  = sscanf(header, selected)
            self.selected = True
        except IncompleteCaptureError, e:
            (self.name,)  = sscanf(header, normal)
            self.selected = False

    #--------------------------------------------------------------------------

    def _parseProcess(self, block):
        """Parse sim process options.
        """
        self.process = SimOptionProcess(block)

    #--------------------------------------------------------------------------

    def _parseInput(self, block):
        """Parse sim input options.
        """
        self.input = SimOptionInput(block)

    #--------------------------------------------------------------------------

    def _parseOutput(self, block):
        """Parse sim output options.
        """
        self.output = SimOptionOutput(block)

#------------------------------------------------------------------------------
# class SimOptionProcess
#------------------------------------------------------------------------------

class SimOptionProcess(Block):
    """Simulation process options.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "brain",
        "cloth",
        "hair",
        "schedule"
    ]

    #--------------------------------------------------------------------------
    # enums
    #--------------------------------------------------------------------------

    class kProcess:
        Brain    = 'brain'
        Cloth    = 'cloth'
        Hair     = 'hair'
        Schedule = 'schedule'

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(SimOptionProcess, self).__init__()
        block = self._removeIndent(block.partition('\n')[2])
        self.parseAttributes(block, SimOptionProcess._sBlockFormatting)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self.printAttributes(SimOptionProcess._sBlockFormatting)
        return "process\n" + self._addIndent(block)

#------------------------------------------------------------------------------
# class SimOptionInput
#------------------------------------------------------------------------------

class SimOptionInput(Block):
    """Simulation input options.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "sims %s %s",      # amc, amc_gz, apf, apf_gz, maya
        "cloth %s %s",     # mgeo, obj
        "hair %s",
        "camera %s"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(SimOptionInput, self).__init__()
        block = self._removeIndent(block.partition('\n')[2])
        self.parseAttributes(block, SimOptionInput._sBlockFormatting)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self.printAttributes(SimOptionInput._sBlockFormatting)
        return "input\n" + self._addIndent(block)

#------------------------------------------------------------------------------
# class SimOptionOutput
#------------------------------------------------------------------------------

class SimOptionOutput(Block):
    """Simulation output options.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "sims %s %s",      # amc, amc_gz, apf, apf_gz, maya, fbx
        "cloth %s %s",     # mgeo, obj
        "hair %s %s",      # mgeo, obj
        "particle %s,"
        "camera %s",
        "callsheet %s",
        "pics %s",
        "ribs %s %s",      # dynamic_load, run_program, 3dl_dynamic_load
        "ribs %s",
        "mi %s",
        "vrscene %s",
        "terrain_map %s",
        "statistics %s",
        "renders %s"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(SimOptionOutput, self).__init__()
        block = self._removeIndent(block.partition('\n')[2])
        self.parseAttributes(block, SimOptionOutput._sBlockFormatting)

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self.printAttributes(SimOptionOutput._sBlockFormatting)
        return "output\n" + self._addIndent(block)

#------------------------------------------------------------------------------
# class PlaceBlock
#------------------------------------------------------------------------------

class PlaceBlock(Block):
    """Placement of generators.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "lock %s",
        "delete %s"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with raw block scene data.
        """
        super(PlaceBlock, self).__init__()

        # [moiz] need to hack this shit since massive files are the most fucked
        #   up files ever!!! argh wtf!!!
        block = block.replace("\nnon_process\n", "\nnon_process\n    ")
        block = block.replace("\nreplay\n", "\nreplay\n    ")

        # initialize fields
        self.groups      = []
        self.generators  = []
        self.non_process = None
        self.replay      = None

        # setup special parse list
        special_list = {
            "group"       : self._parseGroup,
            "generator"   : self._parseGenerator,
            "non_process" : self._parseNonProcess,
            "replay"      : self._parseReplay,
            "lock"        : self._parseAttributeString,
            "delete"      : self._parseAttributeString,
        }

        # setup skip list
        skip_list = ['end']

        # parse the attributes
        self.parseAttributes(
            block, PlaceBlock._sBlockFormatting, special_list, skip_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        groups      = "\n\n".join(map(str, self.groups))
        generators  = "\n".join(map(str, self.generators))
        attributes  = self.printAttributes(PlaceBlock._sBlockFormatting)
        non_process = self._printNonProcess() if self.non_process else ""
        replay      = self._printReplay() if self.replay else ""
        block       = "%s\n%s\n%s" % (groups, generators, attributes)
        return "Place\n%s%s\n%s\nEnd place\n" % \
            (self._addIndent(block), non_process, replay)

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _parseGroup(self, block):
        """Collate all of the groups in the scene.
        """
        self.groups.append(PlaceGroup(block))

    #--------------------------------------------------------------------------

    def _parseGenerator(self, block):
        """Collate all of the generators in the scene.
        """
        self.generators.append(PlaceGenerator(block))

    #--------------------------------------------------------------------------

    def _parseNonProcess(self, block):
        """Collate all of the non process ids in the scene.
        """
        self.non_process = re.findall("\d+", block)

    #--------------------------------------------------------------------------

    def _printNonProcess(self):
        ids = " ".join(self.non_process)
        return "non_process\n%s\nend non_process" % self._addIndent(ids)

    #--------------------------------------------------------------------------

    def _parseReplay(self, block):
        """Collate all of the replay ids in the scene.
        """
        self.replay = re.findall("\d+", block)

    #--------------------------------------------------------------------------

    def _printReplay(self):
        ids = " ".join(self.replay)
        return "replay\n%s\nend replay" % self._addIndent(ids)

#------------------------------------------------------------------------------
# class PlaceGroup
#------------------------------------------------------------------------------

class PlaceGroup(Block):
    """Group of agents in the scene.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "translate %d %d",
        "colour %d",
        "cre %s",
        "cdl %s %d %d",
        "locator_scale %g",
        "place_at_origin",
        "variable %s %f [%f %f] %d %d",
        "variable %s %f [%f %f] %s %d",
        "variable %s %f [%f %f] %s",
        "variable %s %f [%f %f]"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(PlaceGroup, self).__init__()

        # initialize fields
        self.variables = []

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # parse the attributes
        special_list = { "variable" : self._parseVariable }
        self.parseAttributes(block, PlaceGroup._sBlockFormatting, special_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        header     = "group %d %s" % (self.id, self.name)
        attributes = self.printAttributes(PlaceGroup._sBlockFormatting)
        variables  = "\n".join(map(str, self.variables)) + "\n"
        block      = "%s%s" % (attributes, variables)
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Generator block header contains group id and name.
        """
        formating            = "group %d %s"
        (self.id, self.name) = sscanf(header, formating)

    #--------------------------------------------------------------------------

    def _parseVariable(self, block):
        """Collate all of the agent variables for the group.
        """
        formatting = PlaceGroup._sBlockFormatting[6:10]
        data       = self._parseAttributeScanf(block, formatting)
        self.variables.append(Variable(*data))

#------------------------------------------------------------------------------
# class PlaceGenerator
#------------------------------------------------------------------------------

class PlaceGenerator(Block):
    """Generator for creating agents in the scene.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "id       %d",
        "name     %s",
        "centre   %g %g %g",
        "normal   %g %g %g",
        "colour   %g %g %g",
        "radius   %g",
        "number   %d x %d",
        "number   %d",
        "spacing  %g",
        "distance %g",
        "noise    %g %g",
        "angle    %g %g",
        "grid_angle %g",
        "height   %g %g",
        "flow     %d",
        "terrain  %d",
        "row_dist %g",
        "col_dist %g",
        "stagger  %g",
        "grid",
        "points   %d"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(PlaceGenerator, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # parse the attributes
        rest = self.parseAttributes(block, PlaceGenerator._sBlockFormatting)

        # split up the block into lines for easy processing
        lines = rest.split('\n')

        # parse out the points if they are used
        self.point_data = []
        if self.points:
            count           = (self.points + 1) / 2
            self.point_data = lines[:count]
            lines           = lines[count:]

        # this line should be the group line
        self.group = sscanf(lines[0], "groups [%d %d]")

    #--------------------------------------------------------------------------

    def __str__(self):
        header     = "generator %s" % self.type
        attributes = self.printAttributes(PlaceGenerator._sBlockFormatting)
        points     = "\n".join(self.point_data + [""]) if self.points else ""
        group      = "groups [%d %d]" % self.group
        block      = "%s%s%s\n" % (attributes, points, group)
        return "%s\n%send generator" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Generator block header contains generator type.
        """
        formating    = "generator %s"
        (self.type,) = sscanf(header, formating)

