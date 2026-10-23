"""Ember Gate: original early-Ming-inspired game environment.
Run: blender -b -t 8 --python art/build_scene.py -- --draft
Historical and CC0 material references: art/production-notes.md.
"""
import bpy, math, random, os, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
random.seed(1400)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT=os.path.join(ROOT,'art','materials');OUT=os.path.join(ROOT,'dist','assets')
DRAFT='--draft' in sys.argv
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20 if DRAFT else 64
scene.cycles.use_denoising=True;scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=6
scene.render.resolution_x=1400 if DRAFT else 2800;scene.render.resolution_y=788 if DRAFT else 1576;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.31,.39,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.45
coord=bpy.data.objects.new('Material world coordinates',None);scene.collection.objects.link(coord)

def material(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m

def noise_mat(name,color,rough=.7,scale=7,bump=.06):
 m=material(name,color,rough);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');tc.object=coord
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=4;l.new(tc.outputs['Object'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(v*.4 for v in color)+(1,);ramp.color_ramp.elements[1].color=tuple(min(v*1.7,1) for v in color)+(1,);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.6;b.inputs['Distance'].default_value=bump;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal']);return m

def texmat(name,asset,scale=1,sat=1,tint=(1,1,1,1)):
 m=material(name,(.35,.35,.33));n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');tc.object=coord
 v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=scale;l.new(tc.outputs['Object'],v.inputs[0])
 def image(kind):
  path=os.path.join(MAT,f'{asset}_{kind}_2k.jpg');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(path,check_existing=True);t.projection='BOX';t.projection_blend=.08;l.new(v.outputs[0],t.inputs[0]);return t
 t=image('diff');h=n.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=sat;l.new(t.outputs['Color'],h.inputs['Color']);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=tint;l.new(h.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
 r=image('rough');r.image.colorspace_settings.name='Non-Color';l.new(r.outputs[0],p.inputs['Roughness'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.11;l.new(t.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m
brick=texmat('Weathered blue-gray brick • Poly Haven', 'castle_brick_01',.46,.14,(.64,.71,.76,1))
stone=texmat('Basalt foundations • Poly Haven', 'castle_brick_01',.23,.1,(.58,.64,.68,1))
paving=texmat('Worn courtyard stones • Poly Haven','cobblestone_floor_04',.38,.35,(.57,.64,.65,1))
wood=texmat('Aged timber • Poly Haven','wood_planks_dirt',.5,.65,(.55,.39,.24,1))
redwood=noise_mat('Oxide red timber',(.24,.045,.024),.72,8,.025)
roofmats=[noise_mat('Fired gray tile '+str(i),(.09+i*.012,.115+i*.012,.12+i*.012),.4+i*.02,18,.025) for i in range(5)]
edge=noise_mat('Pale cut stone',(.32,.34,.32),.65,9,.07)
iron=noise_mat('Forged iron',(.06,.071,.07),.42,18,.012);iron.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.72
bronze=material('Aged brass',(.36,.22,.08),.35,.7)
dirt=noise_mat('Damp earth',(.07,.067,.044),.85,1.3,.18)
moss=noise_mat('Moss and lichen',(.083,.12,.047),.9,7,.04)
cloth=noise_mat('Weathered vermilion silk',(.32,.025,.013),.95,45,.004)
charcoal=noise_mat('Charred logs',(.018,.014,.009),.93,18,.02)
lightmat=material('Amber flame',(.95,.25,.03));p=lightmat.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.24,.025,1);p.inputs['Emission Strength'].default_value=5
water=material('Moat water',(.022,.055,.045),.16,.3);p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.2
n=water.node_tree.nodes;l=water.node_tree.links;w=n.new('ShaderNodeTexNoise');w.inputs['Scale'].default_value=8;w.inputs['Detail'].default_value=3;b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.09;b.inputs['Strength'].default_value=.3;l.new(w.outputs[0],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])

def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
 if mat: ob.data.materials.append(mat)
 return ob

def cube(name,loc,size,mat,bev=0):
 x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
 ob=mesh(name,vs,[tuple(reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]],mat);ob.location=loc
 if bev:
  m=ob.modifiers.new('Worn edges','BEVEL');m.width=bev;m.segments=2
  m=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return ob

def beam(name,a,b,r,mat,verts=10):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);return o

def tapered(name,cx,cy,w,d,h,z,mat):
 t=.55;vs=[(cx-w/2,cy-d/2,z),(cx+w/2,cy-d/2,z),(cx+w/2,cy+d/2,z),(cx-w/2,cy+d/2,z),(cx-w/2+t,cy-d/2+t,z+h),(cx+w/2-t,cy-d/2+t,z+h),(cx+w/2-t,cy+d/2-t,z+h),(cx-w/2+t,cy+d/2-t,z+h)]
 return mesh(name,vs,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(3,2,1,0)],mat)

# An irregular, fully modeled landscape slice; no photographic backdrop.
N=96;verts=[(0,0,-.25)];ring=[]
for i in range(N):
 a=i/N*math.tau;x=32*math.copysign(abs(math.cos(a))**.55,math.cos(a));y=15.5*math.copysign(abs(math.sin(a))**.55,math.sin(a));v=(x+random.uniform(-.7,.7),y+random.uniform(-.8,.8),random.uniform(-.3,-.1));verts.append(v);ring.append(v)
faces=[(0,i+1,(i+1)%N+1) for i in range(N)]
for v in ring:verts.append((v[0]*.99,v[1]*.99,-1.2-random.random()*.4))
for i in range(N):faces.append((i+1,(i+1)%N+1,(i+1)%N+1+N,i+1+N))
mesh('Broken earth and slate terrain',verts,faces,dirt)
# Stone strips either side of a shallow defense channel.
cube('Moat channel', (0,-8,-.19),(58,4,.14),water)
for y in [-10.1,-5.9]:
 for x in range(-28,29):cube('Moat coping',(x,y,-.02),(.96,.48,.34),stone,.05)
for x in [-18,18]:cube('Courtyard paving',(x,1,-.04),(22,9,.18),paving,.03)
cube('Gate approach paving',(0,-12.4,-.02),(7.5,5,.2),paving,.05)
cube('Inner courtyard',(0,6,-.01),(11,12,.2),paving,.05)
# Bridge with individually weathered planks and pegged railing.
for i in range(20):cube('Bridge oak deck',(0,-10.3+i*.23,.19),(5.7,.215,.21),wood,.025)
for x in [-2.5,2.5]:
 cube('Bridge bearer',(x,-8.1,-.02),(.35,5.1,.45),wood,.025)
 for y in [-10.4,-8.1,-5.9]:
  beam('Bridge rail post',(x,y,.1),(x,y,1.35),.12,wood)
 for z in [.7,1.2]:beam('Bridge rail',(x,-10.4,z),(x,-5.9,z),.08,wood)

# Massive masonry wings and gate body.
for x in [-15,15]:
 tapered('Battered brick rampart',x,0,20,6.5,7.9,0,brick)
 cube('Stone plinth',(x,0,.48),(20.2,6.75,.95),stone,.1)
 cube('Walkway coping',(x,0,8),(19.2,5.6,.3),edge,.06)
 cube('Flagstone wall walk',(x,0,8.2),(18.9,5.2,.15),paving)
 for y in [-2.62,2.62]:
  cube('Crenel breastwork',(x,y,8.65),(19.3,.6,.9),brick,.03)
  for ix in range(15):
   xx=x-9+ix*1.28
   cube('Ming merlon',(xx,y,9.35),(.77,.72,.75),brick,.035)
   cube('Merlon stone cap',(xx,y,9.75),(.88,.84,.14),edge,.025)
 for k in range(8):
  xx=x-9+k*2.55
  cube('Arrow opening shadow',(xx,-3.02,6.9),(.12,.035,.75),charcoal,.012)
  cube('Arrow opening stone sill',(xx,-3.08,6.46),(.37,.2,.1),edge,.02)
 # Bricks with physical depth in foundation courses.
 for row in range(3):
  for i in range(29):
   xx=x-9.8+i*.69+row%2*.34
   cube('Foundation ashlar',(xx,-3.34+row*.03,.16+row*.29),(.66,.18,.27),edge if random.random()<.2 else stone,.025)

gatebody=tapered('Great gate masonry',0,-.3,11.7,8.6,10.25,0,brick)
cube('Gate crown cornice',(0,-.3,10.23),(11,8.15,.44),edge,.08)
# Arch opening boolean: a cylinder rotated along Y plus rectangle below its spring.
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=2.4,depth=13,location=(0,-.3,3.5),rotation=(math.pi/2,0,0));cut=bpy.context.object
mod=gatebody.modifiers.new('Masonry vaulted arch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=gatebody;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
cut=cube('Arch cut',(0,-.3,1.4),(4.8,13,4.2),None)
mod=gatebody.modifiers.new('Gate jamb opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=gatebody;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Radial wedge voussoirs over the entrance, with narrow lime joints.
for i in range(21):
 a=i/21*math.pi+.009;b=(i+1)/21*math.pi-.009
 vs=[]
 for y in [-4.56,-4.28]:
  for r,t in [(2.4,a),(2.96,a),(2.96,b),(2.4,b)]:vs.append((r*math.cos(t),y,3.5+r*math.sin(t)))
 ob=mesh('Cut stone arch voussoir',vs,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],edge if i%4 else stone)
for x in [-2.68,2.68]:
 for z in range(7):cube('Gate jamb block',(x,-4.36,.26+z*.5),(.55,.4,.48),edge,.02)
# Arched doors with separate leaves, physical hinges and iron studs.
doors=[]
for side in [-1,1]:
 pivot=bpy.data.objects.new('Left oak gate hinge' if side<0 else 'Right oak gate hinge',None);scene.collection.objects.link(pivot);pivot.location=(side*2.34,-3.72,0);doors.append(pivot);bpy.context.view_layer.update()
 for i in range(8):
  x=side*(.15+i*.29);height=3.5+math.sqrt(max(0,2.34**2-x*x))-.08
  o=cube('Heavy vertical gate plank',(x,-3.72,height/2),(.277,.28,height),wood,.025);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
 for z in [.7,2.0,3.3]:
  o=cube('Wrought iron gate strap',(side*1.17,-3.9,z),(2.28,.08,.15),iron,.02);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
 for xi in range(5):
  for zi in range(6):
   o=sphere('Iron gate stud',(side*(.25+xi*.43),-3.97,.5+zi*.67),(.07,.04,.07),bronze);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
 o=sphere('Gate ring boss',(side*.38,-4.02,2.4),(.16,.06,.2),bronze);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
 bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=6,location=(side*.38,-4.08,2.25),major_radius=.16,minor_radius=.035,rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.materials.append(iron);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
# Dark tunnel road; small crossbar details around the hall.
cube('Tunnel paving',(0,-.3,.04),(4.7,8.7,.18),paving)
cube('Gate identification tablet',(0,-4.04,7.8),(2.8,.2,.85),wood,.06)
for x in [-.76,0,.76]:
 cube('Tablet bronze vertical mark',(x,-4.17,7.83),(.09,.02,.52),bronze,.01)
 for z in [7.65,7.9]:cube('Tablet bronze horizontal mark',(x,-4.17,z),(.4,.025,.055),bronze,.01)

# Roofs: curved hip surfaces, overlapping ceramic tile courses and raised ridges.
def roof(name,cx,cy,w,d,z,h):
 ridge=w*.28
 corners=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
 tops=[(-ridge,0),(ridge,0),(ridge,0),(-ridge,0)]
 # Each face extends between a ridge edge (or point) and an eave edge.
 for f in range(4):
  a=corners[f];b=corners[(f+1)%4];ta=tops[f];tb=tops[(f+1)%4]
  nu=max(9,int(math.dist(a,b)/.19));nv=max(9,int(d/.24));vs=[];fs=[]
  def pos(u,t,extra=0):
   ex=a[0]*(1-u)+b[0]*u;ey=a[1]*(1-u)+b[1]*u;rx=ta[0]*(1-u)+tb[0]*u;ry=ta[1]*(1-u)+tb[1]*u
   zz=z+h*(1-t)**1.55+.28*t**6+.5*abs(2*u-1)**8*t**4+extra
   return (cx+rx*(1-t)+ex*t,cy+ry*(1-t)+ey*t,zz)
  for j in range(nv+1):
   t=j/nv
   for i in range(nu+1):vs.append(pos(i/nu,t,.035*math.cos((i%2)*math.pi)))
  for j in range(nv):
   for i in range(nu):
    k=j*(nu+1)+i;fs.append((k,k+1,k+nu+2,k+nu+1))
  ob=mesh(name+' curved roof',vs,fs,roofmats[1]);sol=ob.modifiers.new('Ceramic thickness','SOLIDIFY');sol.thickness=.055
  # Raised tubular tile ribs and overlapping horizontal seams, a single mesh per roof face.
  vs=[];fs=[]
  for i in range(nu+1):
   u=i/nu
   for j in range(nv):
    t0=j/nv;t1=min(1,(j+1.07)/nv);p0=Vector(pos(u,t0,.055));p1=Vector(pos(u,t1,.055));direction=(p1-p0).normalized();sidev=direction.cross(Vector((0,0,1))).normalized();up=sidev.cross(direction).normalized();base=len(vs)
    for p in [p0,p1]:
     for k in range(7):
      angle=k/6*math.pi;v=p+sidev*(math.cos(angle)*.075)+up*(math.sin(angle)*.07);vs.append(tuple(v))
    for k in range(6):fs.append((base+k,base+k+1,base+k+8,base+k+7))
  o=mesh(name+' individual barrel tiles',vs,fs,roofmats[2]);[o.data.materials.append(m) for m in roofmats]
  for poly in o.data.polygons:poly.material_index=random.randrange(len(o.data.materials)) if random.random()<.15 else 0
  # Eaves in dark timber with curved upturned corners.
  last=None
  for i in range(25):
   p=pos(i/24,1,-.13)
   if last:beam('Curved fascia',last,p,.105,wood,6)
   last=p
  # Hip tile ridges.
  last=None
  for j in range(14):
   p=pos(0,j/13,.1)
   if last:beam('Raised hip ridge',last,p,.12,roofmats[3],8)
   last=p
 beam('Main roof ridge',(cx-ridge,cy,z+h+.12),(cx+ridge,cy,z+h+.12),.16,roofmats[3],10)
 for side in [-1,1]:
  x=cx+ridge*side
  beam('Raised ridge end',(x,cy,z+h+.15),(x+side*.25,cy,z+h+.65),.12,roofmats[3],8)
  sphere('Ridge guardian finial',(x+side*.25,cy,z+h+.62),(.24,.16,.25),roofmats[3])

def pavilion(name,cx,cy,w,d,z,h):
 cube(name+' timber hall',(cx,cy,z+h/2),(w-.9,d-.8,h),redwood,.025)
 # Wooden paneling and fine lattice window bars.
 for face in [-1,1]:
  yy=cy+face*(d/2-.38)
  for ix in range(5):
   xx=cx+(ix-2)*(w/5.4)
   cube('Shadow behind window',(xx,yy+face*.03,z+h*.55),(w/6,.08,h*.5),charcoal,.02)
   for j in range(7):cube('Window lattice upright',(xx-w/12+j*w/36,yy+face*.1,z+h*.55),(.035,.05,h*.51),wood)
   for j in range(4):cube('Window lattice crosspiece',(xx,yy+face*.11,z+h*.31+j*h*.16),(w/6,.055,.045),wood)
 for xx in [cx-w/2,cx-w/4,cx,cx+w/4,cx+w/2]:
  for yy in [cy-d/2,cy+d/2]:
   beam('Vermilion timber column',(xx,yy,z),(xx,yy,z+h),.15,redwood,12)
   cube('Stone column plinth',(xx,yy,z+.08),(.43,.43,.2),edge,.05)
   for k in range(3):
    zz=z+h-.4+k*.19
    cube('Layered timber bracket',(xx,yy,zz),(.47+k*.24,.32,.15),redwood,.025)
    cube('Projecting bracket arm',(xx,yy,zz+.08),(.18,.6+k*.23,.13),wood,.02)
 for yy in [cy-d/2,cy+d/2]:
  cube('Gilded lintel beam',(cx,yy,z+h-.1),(w+.35,.28,.26),redwood,.035)
  cube('Timber gallery rail',(cx,yy,z+.85),(w+.3,.12,.12),redwood,.02)
  for i in range(int(w/.35)):
   cube('Gallery baluster',(cx-w/2+i*.35,yy,z+.45),(.055,.07,.8),redwood,.01)
 roof(name,cx,cy,w+2,d+2,z+h,2.0 if w>8 else 1.5)

# The two-story central gate pavilion has a generous lower roof and raised upper hall.
pavilion('Lower gatehouse',0,-.3,9.7,6.8,10.5,2.5)
pavilion('Upper gatehouse',0,-.3,7.3,4.9,14.5,2.5)
for x in [-22.1,22.1]:
 tapered('Flanking watchtower',x,0,6.7,7.7,10.2,0,brick)
 cube('Tower foundation',(x,0,.5),(6.9,7.9,1),stone,.08)
 cube('Tower platform stone cornice',(x,0,10.25),(6.5,7.5,.35),edge,.06)
 pavilion('Watchtower pavilion',x,0,4.8,5.4,10.5,2.8)
 for xx in [-1.45,0,1.45]:
  cube('Tower arrow opening',(x+xx,-3.55,7.1),(.16,.05,1.15),charcoal,.03)
  cube('Tower arrow sill',(x+xx,-3.59,6.49),(.48,.19,.15),edge,.03)

# Cloth banners and their crossarms; asymmetric wind creates folds.
def flag(x,y,z,side=1):
 beam('Banner pole',(x,y,z-3.2),(x,y,z+.9),.065,wood)
 beam('Banner crossarm',(x-.6,y,z),(x+.7,y,z),.04,bronze)
 vs=[];fs=[];nx=10;ny=20
 for j in range(ny+1):
  for i in range(nx+1):
   u=i/nx;v=j/ny;vs.append((x+(u-.5)*1.22,y+.15*math.sin(u*7+v*5)*v+v*.17,z-v*2.6+(.09*math.sin(u*6) if j==ny else 0)))
 for j in range(ny):
  for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
 mesh('Wind-folded red banner',vs,fs,cloth)
 for xx in [-.51,.51]:beam('Banner ochre border',(x+xx,y-.01,z),(x+xx,y+.15,z-2.5),.025,bronze,6)
for x in [-18,-7,7,18]:flag(x,-1.9,12.3)

# Braziers and light pool sources. Positions also feed the 2D ember renderer.
flame_positions=[]
def brazier(x,y,z):
 for a in range(3):
  angle=a*math.tau/3;beam('Brazier tripod',(x+math.cos(angle)*.32,y+math.sin(angle)*.32,z),(x+math.cos(angle)*.14,y+math.sin(angle)*.14,z+1.3),.055,iron)
 bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.25,radius2=.45,depth=.25,location=(x,y,z+1.3));bpy.context.object.data.materials.append(iron)
 for i in range(5):
  ob=sphere('Brazier flame',(x+random.uniform(-.18,.18),y+random.uniform(-.18,.18),z+1.58),(.08,.1,random.uniform(.22,.42)),lightmat)
 flame_positions.append((x,y,z+1.65))
 data=bpy.data.lights.new('Firelight','POINT');data.energy=180;data.color=(1,.22,.035);data.shadow_soft_size=.6;o=bpy.data.objects.new('Firelight',data);scene.collection.objects.link(o);o.location=(x,y,z+1.9)
for x,y,z in [(-3.8,-5.1,0),(3.8,-5.1,0),(-8,-1.1,8.3),(8,-1.1,8.3),(-21,1.5,10.5),(21,1.5,10.5)]:brazier(x,y,z)

# Supplies, bundled arrows, timber barricades, and small tools provide human scale.
for x,y in [(-11,1),(-12.5,1.2),(10,1.5),(11.3,1.7),(-4,8),(5,8.5)]:
 zz=8.3 if abs(x)>8 else .1
 cube('Supply crate',(x,y,zz+.35),(1,.7,.7),wood,.025)
 for dz in [.08,.6]:cube('Crate iron band',(x,y-.36,zz+dz),(1.03,.035,.06),iron)
 for dx in [-.42,.42]:cube('Crate upright',(x+dx,y-.39,zz+.35),(.08,.08,.75),wood,.01)
for x,y in [(-11,-12),(12,-12),(-21,-11),(22,-11)]:
 beam('Barricade stretcher',(x-2,y,.75),(x+2,y,.75),.12,wood)
 for dx in [-1.7,-.85,0,.85,1.7]:
  for d in [-1,1]:
   a=(x+dx,y-d*.55,.05);b=(x+dx,y+d*.6,1.6);beam('Pointed timber barricade',a,b,.095,wood,7)
   vec=(Vector(b)-Vector(a)).normalized();tip=Vector(b)+vec*.3
   bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.096,radius2=0,depth=.3,location=(Vector(b)+tip)/2);o=bpy.context.object;o.rotation_euler=vec.to_track_quat('Z','Y').to_euler();o.data.materials.append(wood)
# Rocks and plants around the base; keep roadway and water clear.
for i in range(125):
 x=random.uniform(-29,29);y=random.uniform(-14,13)
 if abs(x)<5 or (-10.6<y<4.4):continue
 o=sphere('Weathered loose stone',(x,y,-.03),(random.uniform(.09,.5),random.uniform(.08,.35),random.uniform(.08,.3)),stone);o.rotation_euler=(random.random(),random.random(),random.random())
vs=[];fs=[]
for i in range(1100):
 x=random.uniform(-29,29);y=random.uniform(-14,13)
 if abs(x)<5 or (-10.5<y<4 and abs(x)<26):continue
 if random.random()<.25:continue
 for k in range(4):
  a=random.random()*math.tau;h=random.uniform(.16,.55);w=.035;idx=len(vs);vs.extend([(x-w*math.cos(a),y-w*math.sin(a),-.08),(x+w*math.cos(a),y+w*math.sin(a),-.08),(x+.17*math.cos(a),y+.17*math.sin(a),h)]);fs.append((idx,idx+1,idx+2))
mesh('Wild grass and reeds',vs,fs,moss)
# A few vegetation patches follow the damp stone wall base.
for i in range(45):
 x=random.uniform(-26,26)
 if abs(x)<6:continue
 sphere('Moss beside foundation',(x,random.uniform(-4.4,-3.3),-.08),(random.uniform(.2,.65),random.uniform(.1,.35),.12),moss)

# Low warm sun with large blue fill makes real occlusion, softened by overcast sky.
def area(name,loc,power,color,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Evening key',(-20,-30,36),8500,(1,.7,.42),18,(0,0,6))
area('Cool sky fill',(18,10,35),9500,(.45,.65,1),22,(0,0,5))
d=bpy.data.lights.new('Last sunlight','SUN');d.energy=1.5;d.angle=.14;d.color=(1,.8,.59);o=bpy.data.objects.new('Last sunlight',d);scene.collection.objects.link(o);o.rotation_euler=(math.radians(28),math.radians(-20),math.radians(-30))
# Orthographic 2.5D camera, with enough front face to read the fortifications.
data=bpy.data.cameras.new('Isometric camera');cam=bpy.data.objects.new('Isometric camera',data);scene.collection.objects.link(cam);cam.location=(36,-62,45);target=Vector((0,0,5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=73;scene.camera=cam
bpy.context.view_layer.update()
def project(p):
 v=world_to_camera_view(scene,cam,Vector(p));return [round(v.x*1672,2),round((1-v.y)*941,2)]
pts={
 'west':{'point':(-22.1,-.5,12.4),'bounds':[(-25.6,-4,0),(-18.6,-4,0),(-18.6,4,15.2),(-25.6,4,15.2)]},
 'wall':{'point':(-12,-3.3,5),'bounds':[(-18,-3.4,0),(-6,-3.4,0),(-6,-3.4,9.5),(-18,-3.4,9.5)]},
 'gate':{'point':(0,-4.3,4.2),'bounds':[(-3,-4.5,0),(3,-4.5,0),(3,-4.5,6.8),(-3,-4.5,6.8)]},
 'east':{'point':(22,-.4,12.4),'bounds':[(18.5,-4,0),(25.6,-4,0),(25.6,4,15.2),(18.5,4,15.2)]},
 'utilities':{'point':(0,-.3,16.1),'bounds':[(-6,-4.5,10.5),(6,-4.5,10.5),(6,4,19),(-6,4,19)]},
 'catwalk':{'point':(0,-8,.6),'bounds':[(-3,-10.5,0),(3,-10.5,0),(3,-5.5,1.4),(-3,-5.5,1.4)]}
}
meta={'width':1672,'height':941,'flames':[project(p) for p in flame_positions],'parts':{k:{'point':project(v['point']),'polygon':[project(p) for p in v['bounds']]} for k,v in pts.items()}}
with open(os.path.join(OUT,'scene-map.json'),'w') as f:json.dump(meta,f)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'art','ember-gate.blend'))
scene.render.filepath=os.path.join(OUT,'ming-draft.png' if DRAFT else 'ming-closed.png');bpy.ops.render.render(write_still=True)
if not DRAFT:
 for i,pivot in enumerate(doors):pivot.rotation_euler.z=math.radians(76 if i==0 else -76)
 scene.render.filepath=os.path.join(OUT,'ming-open.png');bpy.ops.render.render(write_still=True)
print('EMBER_GATE_RENDER_COMPLETE')
