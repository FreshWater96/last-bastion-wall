"""Finalize a saved Ember Gate scene and render its two gate states."""
import bpy, os, math, sys, bmesh
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene=bpy.context.scene
# Correct inverse bind transforms for every door component before either state.
for name in ['Left oak gate hinge','Right oak gate hinge']:
 pivot=bpy.data.objects[name];pivot.rotation_euler.z=0
 bpy.context.view_layer.update()
 for child in pivot.children:child.matrix_parent_inverse=pivot.matrix_world.inverted()

# Reconstruct the arch as one watertight cutter, extending all the way to the ground.
old=bpy.data.objects['Great gate masonry'];mat=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
w,d,h,z,cx,cy,t=11.7,8.6,10.25,0,0,-.3,.55
vs=[(cx-w/2,cy-d/2,z),(cx+w/2,cy-d/2,z),(cx+w/2,cy+d/2,z),(cx-w/2,cy+d/2,z),(cx-w/2+t,cy-d/2+t,z+h),(cx+w/2-t,cy-d/2+t,z+h),(cx+w/2-t,cy+d/2-t,z+h),(cx-w/2+t,cy+d/2-t,z+h)]
me=bpy.data.meshes.new('Gate solid');me.from_pydata(vs,[],[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(3,2,1,0)]);me.update();gate=bpy.data.objects.new('Great gate masonry',me);scene.collection.objects.link(gate);me.materials.append(mat)
outline=[(-2.4,-.5),(2.4,-.5)]+[(2.4*math.cos(i/32*math.pi),3.5+2.4*math.sin(i/32*math.pi)) for i in range(33)]
N=len(outline);vs=[(x,y,z) for y in [-8,8] for x,z in outline];fs=[tuple(range(N)),tuple(reversed(range(N,2*N)))]+[(i,N+i,N+(i+1)%N,(i+1)%N) for i in range(N)]
me=bpy.data.meshes.new('Full arch cutter');me.from_pydata(vs,[],fs);me.update();cutter=bpy.data.objects.new('Full arch cutter',me);scene.collection.objects.link(cutter)
mod=gate.modifiers.new('Vaulted gate passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=gate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Recalculate outward normals for closed components authored by the scene builder.
for me in bpy.data.meshes:
 if len(me.vertices)==8 and len(me.polygons)==6:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()

# Broad, subtle water staining in the scanned brick material.
m=bpy.data.materials['Weathered blue-gray brick • Poly Haven'];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');previous=p.inputs['Base Color'].links[0].from_socket
coord=n.new('ShaderNodeTexCoord');coord.object=bpy.data.objects['Material world coordinates'];v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(1.4,1.4,.085);l.new(coord.outputs['Object'],v.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=4;l.new(v.outputs[0],noise.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.3;ramp.color_ramp.elements[0].color=(.42,.46,.4,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.64;l.new(previous,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
scene.render.resolution_x=2800;scene.render.resolution_y=1576;scene.cycles.samples=64
if '--review' in sys.argv:scene.render.resolution_x=1400;scene.render.resolution_y=788;scene.cycles.samples=16
scene.render.filepath=os.path.join(ROOT,'dist/assets/ming-review.png' if '--review' in sys.argv else 'dist/assets/ming-closed.png');bpy.ops.render.render(write_still=True)
if '--review' in sys.argv:sys.exit(0)
for i,name in enumerate(['Left oak gate hinge','Right oak gate hinge']):bpy.data.objects[name].rotation_euler.z=math.radians(76 if i==0 else -76)
scene.render.filepath=os.path.join(ROOT,'dist/assets/ming-open.png');bpy.ops.render.render(write_still=True)
print('FINAL_STATES_COMPLETE')
