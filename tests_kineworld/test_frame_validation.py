"""Execute the real argument validator without importing heavyweight GPU modules."""
import ast
from pathlib import Path
import random
import sys
from types import SimpleNamespace as NS
import unittest


class FrameTests(unittest.TestCase):
    def setUp(self):
        source=ast.parse((Path(__file__).resolve().parents[1]/'generate.py').read_text(encoding='utf-8'))
        fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='_validate_args')
        cfg=NS(sample_steps=4,sample_shift=5,sample_guide_scale=1,frame_num=81)
        self.scope=dict(WAN_CONFIGS={'ti2v-5B':cfg},EXAMPLE_PROMPT={'ti2v-5B':{'prompt':'x'}},SUPPORTED_SIZES={'ti2v-5B':['1280*704']},sys=sys,random=random)
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'generate.py','exec'),self.scope)

    def args(self,n):
        return NS(ckpt_dir='fixture',task='ti2v-5B',prompt='test',image=None,audio=None,enable_tts=False,tts_prompt_audio=None,tts_text=None,sample_steps=None,sample_shift=None,sample_guide_scale=None,frame_num=n,base_seed=42,size='1280*704')

    def test_invalid_frames_fail_before_model_loading(self):
        for n in (0,-3,2,4,80):
            with self.subTest(n=n),self.assertRaises(ValueError):self.scope['_validate_args'](self.args(n))

    def test_valid_and_default_frames_are_preserved(self):
        for n in (1,5,81,None):
            a=self.args(n);self.scope['_validate_args'](a)
            self.assertEqual(a.frame_num,81 if n is None else n)

if __name__=='__main__':unittest.main()
