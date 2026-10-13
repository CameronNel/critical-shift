"""Unsupported light closures must fail before an import can drop or reinterpret them."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as N

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mine_context_lights import context_spot_lights


def light():
    emission=N(type="EMISSION",inputs={
        "Color":N(is_linked=False,default_value=(1,1,1,1)),
        "Strength":N(is_linked=False,default_value=1)})
    output=N(type="OUTPUT_LIGHT",is_active_output=True,inputs={"Surface":N(links=[N(from_node=emission)])})
    data=N(type="SPOT",normalize=True,use_soft_falloff=True,exposure=0,use_temperature=False,
        diffuse_factor=1,specular_factor=1,volume_factor=1,use_nodes=True,node_tree=N(nodes=[emission,output]),
        color=(1,.92,.78),energy=2600,shadow_soft_size=.12,spot_size=2.1816616058,spot_blend=.8)
    return N(type="LIGHT",name="LIGHT_pole_1",hide_render=False,data=data)


def matrix(_):
    return N(translation=(1,2,3),to_quaternion=lambda:(1,0,0,0))


class ContextSpotGuardTests(unittest.TestCase):
    def test_neutral_closure_retains_source_pose_and_cone(self):
        record=context_spot_lights([light()],matrix)[0]
        self.assertEqual(record["position"],[1,2,3])
        self.assertEqual(record["rotation"],[1,0,0,0])
        self.assertEqual(record["spotBlend"],.8)
        self.assertTrue(record["normalized"] and record["softFalloff"])

    def test_unsupported_emitter_modifiers_reject(self):
        for key,value in [("normalize",False),("use_soft_falloff",False),("exposure",1),
                ("use_temperature",True),("diffuse_factor",.5),("specular_factor",.5),("volume_factor",.5)]:
            with self.subTest(key=key):
                o=light();setattr(o.data,key,value)
                with self.assertRaisesRegex(ValueError,"modifiers"):
                    context_spot_lights([o],matrix)

    def test_coloured_or_linked_emission_rejects(self):
        for key,value in [("Color",(1,.8,1,1)),("Strength",2)]:
            with self.subTest(key=key):
                o=light();o.data.node_tree.nodes[0].inputs[key].default_value=value
                with self.assertRaisesRegex(ValueError,"emission"):
                    context_spot_lights([o],matrix)
        o=light();o.data.node_tree.nodes[0].inputs["Strength"].is_linked=True
        with self.assertRaisesRegex(ValueError,"emission"):context_spot_lights([o],matrix)

    def test_missing_or_unsupported_active_closure_rejects(self):
        o=light();o.data.node_tree.nodes[1].is_active_output=False
        with self.assertRaisesRegex(ValueError,"closure"):context_spot_lights([o],matrix)
        o=light();o.data.node_tree.nodes[0].type="BLACKBODY"
        with self.assertRaisesRegex(ValueError,"closure"):context_spot_lights([o],matrix)

    def test_nonphysical_and_nonfinite_parameters_reject(self):
        for key,value in [("energy",float("nan")),("energy",-1),("shadow_soft_size",0),
                ("spot_size",0),("spot_blend",0),("spot_blend",1.1),("color",(1,float("inf"),1))]:
            with self.subTest(key=key):
                o=light();setattr(o.data,key,value)
                with self.assertRaisesRegex(ValueError,"parameters"):
                    context_spot_lights([o],matrix)

    def test_duplicate_identities_reject(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            context_spot_lights([light(),light()],matrix)

    def test_hidden_spots_are_omitted(self):
        o=light();o.hide_render=True
        self.assertEqual(context_spot_lights([o],matrix),[])
