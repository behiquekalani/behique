# 3D Fashion Design: From Concept to Game-Ready Assets

*Create Professional Digital Clothing for Games and Virtual Worlds*

**By Behike**

Price: $9.99

---

## Legal Notice

Copyright 2026 Behike. All rights reserved.

No part of this publication may be reproduced, distributed, or transmitted in any form without prior written permission of the publisher.

**AI Disclosure:** This book was written with AI assistance. All content is original and does not reproduce any copyrighted material.

---

## Table of Contents

1. [The Digital Fashion Pipeline](#the-digital-fashion-pipeline)
2. [Cloth Simulation Fundamentals](#cloth-simulation-fundamentals)
3. [Mastering Folds, Layers, and Fit](#mastering-folds-layers-and-fit)
4. [Topology, Retopology, and Game-Ready Meshes](#topology-retopology-and-game-ready-meshes)
5. [Texturing, Detailing, and Final Presentation](#texturing-detailing-and-final-presentation)

---

## Chapter 1: The Digital Fashion Pipeline

Building digital clothing is not modeling. It is engineering fabric.

The difference matters. A 3D modeler sculpts shapes. A digital fashion designer simulates real materials under real forces, then optimizes the result for a specific platform. The process bridges fashion design, physics simulation, and game art.

**The Core Tools**

The modern digital fashion pipeline uses three primary tools.

Marvelous Designer handles cloth simulation. You draw 2D patterns (like a tailor cutting fabric), define how those patterns sew together, and let the physics engine drape them over a virtual body. The software simulates gravity, collision, and material properties to produce realistic folds.

ZBrush handles sculpting and detail. After simulation, you export your garments and refine them. Fix unrealistic folds, add micro-details the simulation missed, and adjust the silhouette for visual appeal.

A traditional 3D package (Maya, Blender, or 3ds Max) handles retopology, UV layout, and final export. This is where you optimize the mesh for game engines.

Some artists also use Substance Painter or Marmoset Toolbag for texturing and rendering, but the core pipeline is pattern, simulate, sculpt, retopologize, texture.

**Essential Terminology**

Before you touch any software, learn the language.

A garment is any clothing item. A pattern is the 2D, flat, unwrapped version of your garment, made up of separate panels. Think of patterns like UV layouts for cloth.

Sewing is the act of connecting two panel edges. Seams are the visible details that sewing creates, from stitch lines to folded edges.

Simulation is a computer algorithm faking real-world forces. It is not physically accurate. It is a tool that produces results you then refine by hand.

Particle distance controls mesh resolution during simulation. Lower values create denser meshes with more detail but slower computation. Work at high particle distances (20mm) while fitting, then decrease (5mm or lower) for final folds.

**Material Properties**

Fabric behavior in simulation depends on three directional properties.

Weft is the horizontal weave. Adjusting weft shrinkage changes how much fabric compresses or stretches side to side.

Warp is the vertical weave. Same concept, vertical direction.

Bias is the 45-degree diagonal between weft and warp. Adjusting bias produces specific fold patterns common in fabrics like denim.

These are not abstract settings. They are the digital equivalent of choosing cotton versus leather versus silk. A leather jacket and a silk blouse use the same software but produce completely different results because of these material properties.

**Reference is Everything**

Never start a garment without reference. You need four categories.

Pattern reference shows you how the 2D panels should look. Fashion sewing books and pattern-making resources are invaluable here.

Fit reference shows how the garment sits on a body. How loose are the sleeves? Where does the hem hit? How much drape at the waist?

Detail reference shows close-up construction. Stitch types, seam finishes, zipper placement, elastic behavior.

Style reference shows the overall aesthetic. This is the target you are aiming for.

Collect all four before opening any software. The time you spend gathering reference saves triple the time in production.

### Exercises

- [ ] Identify the 3 primary tools in the digital fashion pipeline and install at least the simulation tool
- [ ] Create a reference folder with 4 subfolders: Pattern, Fit, Detail, Style
- [ ] Collect at least 5 reference images for a simple t-shirt across all 4 categories
- [ ] Define weft, warp, and bias in your own words without looking at the chapter
- [ ] List 3 real-world fabrics and describe how they would differ in simulation settings

---

## Chapter 2: Cloth Simulation Fundamentals

Simulation is where digital fashion begins. You draw flat patterns, sew them together, and let physics create the garment.

**Setting Up Your Workspace**

When you first open your simulation software, configure units to centimeters. This matters because all measurements, from pattern dimensions to particle distance, depend on consistent units.

Import your base avatar. This is the body your clothing will drape over. Set the scale to centimeters on import. Enable automatic arrangement points, which are snap locations on the body that help you place patterns quickly.

Save your project immediately. Save often. Simulation software can be unstable with complex garments.

**Drawing Patterns**

The 2D viewport is your pattern table. Use the polygon tool to draw outlines. Start simple. A basic shirt front panel needs five points: neckline, shoulder, armhole bottom, hem corner, and center.

Draw half the pattern and mirror it for symmetry. This ensures both sides match perfectly and lets you edit both sides simultaneously.

Add curvature to straight lines for natural-looking edges. Armholes and necklines are never straight on real garments.

**Sewing Panels Together**

Select the sewing tool. Click the first edge, then click the matching edge on the other panel. Lines appear between them showing the connection.

If the sewing lines cross, the panels will twist during simulation. Reverse the sewing direction to fix this.

Sew side seams first, then shoulders, then sleeves. This order makes debugging easier because you can simulate after each step and catch problems early.

**Your First Simulation**

Before pressing simulate, arrange your patterns around the avatar. Use arrangement points to snap panels to the correct body part, front panel to the torso front, back panel to the torso back, sleeves to the arms.

Give patterns some space away from the body. Gravity pulls everything down during the first few frames of simulation. If patterns start too close, they collide with the body and create artifacts.

Press the simulate button or spacebar. The garment falls, wraps, and settles. Use the grab tool to adjust fit while simulation runs.

If simulation is slow, switch to GPU processing. It is less accurate but significantly faster for real-time adjustments.

**Building a Shirt from Scratch**

Start with the front panel. Draw half, mirror it. Adjust the neckline depth and shoulder width by moving points.

Create the back panel by copying and flipping the front. Lower the back neckline slightly, raise it in front. Real shirts have different front and back necklines.

For sleeves, measure the armhole length on your body panels. Create a rectangle with the top edge matching that length. Taper the bottom edge to match wrist circumference. Add a bump at the top for the shoulder cap.

Sew the sleeve to the armhole using the free sewing tool for curved seams. Start from the bottom of the armhole, trace up to the shoulder on the body, then trace around the sleeve cap.

Mirror the sleeve for the other arm. Simulate. Adjust.

**Internal Lines and Seam Details**

Select an edge and offset it inward to create an internal line. This represents a hem fold or decorative seam.

Set the fold angle on internal lines to control how the fabric behaves at the seam. Zero degrees pushes outward. 180 degrees stays flat. 360 degrees pushes inward (like a folded hem).

Increase fold strength to make the fold more pronounced. Real garments have visible seam ridges. These small details separate amateur work from professional.

**Working with Layers**

When building multi-piece outfits (a jacket over a shirt), freeze the inner garment before simulating the outer one. This preserves the inner garment's folds while allowing the outer garment to drape naturally over it.

Use the layer property to control which garment sits on top when panels overlap. Higher layer numbers sit on top. Reset layers to zero after resolving conflicts, or strange simulation artifacts can appear.

**Scaling for Higher Resolution**

Here is a technique that dramatically increases fold detail without changing your particle distance settings.

Scale your avatar and patterns to 200%. Import or resize the avatar at double size, then use auto-fitting to rescale all patterns to match. The garment is now twice as large, which means the same particle distance captures twice the detail.

A jacket at 100% scale with 5mm particle distance produces around 450,000 triangles. The same jacket at 200% scale with the same particle distance produces around 900,000 triangles. The extra triangles mean crisper folds, visible secondary wrinkles, and hints of tertiary detail near seams.

When you export, set the scale percentage to 50% to bring everything back to normal size. The detail stays.

This technique is especially useful when you want to minimize your sculpting pass. More detail from simulation means less time fixing things by hand.

**Fabric Presets and Libraries**

Most simulation software comes with material presets: cotton, silk, leather, denim, nylon, wool. These presets configure all the physical properties (stiffness, weight, friction, shrinkage) to approximate real fabrics.

Start with presets. Then adjust. No preset perfectly matches every garment. A heavy winter coat cotton behaves differently from a lightweight summer cotton. Tweak the bending stiffness, increase the weight, and adjust shrinkage until the fold behavior matches your reference.

Save your custom settings as new presets. Over time, you build a personal fabric library that matches your style and the type of work you do. This library becomes one of your most valuable assets.

**Common Simulation Problems**

Parts clipping through the avatar: increase collision thickness or add more space between the pattern and the body before simulating.

Garments falling to the floor: you forgot to sew the panels together. Check all seam connections.

Strange pulling or twisting: sewing direction is reversed on one or more seams. Open the sewing editor and reverse the problematic connections.

Slow simulation: reduce the number of active patterns. Freeze garments you are not currently editing. Switch to GPU processing for real-time adjustments.

Unrealistic fold shapes: your material settings do not match the fabric you are targeting. Check your reference and adjust shrinkage, bending, and weight accordingly.

### Exercises

- [ ] Draw a symmetric front panel for a basic t-shirt using 5 control points
- [ ] Create front, back, and two sleeve panels, sew them together, and run a simulation
- [ ] Add internal lines to the hem and neckline with fold angles of 300 degrees
- [ ] Adjust shrinkage settings (weft and warp) to create a loose vs. fitted look on the same pattern
- [ ] Freeze a shirt garment and simulate a jacket over it

---

## Chapter 3: Mastering Folds, Layers, and Fit

Simulation gives you folds. Your job is to make them look right.

**Understanding Fold Types**

Folds are not random. They follow physical rules that you can learn to predict and control.

Primary folds are large, structural. They appear where gravity pulls excess fabric downward or where fabric bunches against a surface. The large drapes at the bottom of an untucked shirt. The gathering under the arm of a jacket.

Secondary folds are smaller and form between primary folds. They appear when you increase resolution or add more fabric. The wrinkles between the big folds.

Tertiary folds are micro-details. Fine wrinkles, fabric memory lines, the tiny creases that appear at stress points. Simulation rarely produces these at standard resolution. You add them in the sculpting phase.

**Fold Appeal**

Technical accuracy is not enough. Folds need appeal.

Study reference constantly. Real fabric does not fold symmetrically. Folds cluster around tension points (elbows, shoulders, waistbands) and thin out across relaxed surfaces (the chest of a loose shirt, the back of a long coat).

Break up parallel lines. Three folds running perfectly parallel look artificial. Vary the spacing, depth, and direction slightly.

Folds should tell a story about the garment. Tight fabric has small, numerous folds. Loose fabric has large, sweeping folds. Heavy fabric drapes in broad curves. Light fabric bunches in tight clusters.

**Controlling Fit Through Pattern Adjustment**

The size and shape of your patterns determine everything about fit. There are two approaches.

Pattern scaling: increase or decrease the overall size. A 105% scale creates a slightly loose fit. A 95% scale creates a tighter fit.

Shrinkage adjustment: use weft and warp shrinkage to add or remove fabric without changing pattern dimensions. Warp shrinkage above 100% adds vertical fabric, creating more folds from shoulder to hem. Weft shrinkage above 100% adds horizontal fabric, creating more folds around the torso.

Both approaches produce different fold characteristics. Experiment to find what matches your reference.

**Building Complex Garments**

A puffer jacket, a multi-layer outfit, a coat with collar and cuffs. Complex garments are just simple garments stacked and connected.

Start with the body. Fit it well. Freeze it. Add the collar as a separate panel set, sewn to the neckline with a stiffer material. Add cuffs as small rectangles with elastic shrinkage, sewn to the sleeve ends. Add a zipper stand as a narrow strip, sewn along the front opening.

Each component uses a different material preset. The body uses a soft cotton or nylon. The collar and cuffs use a stiffer trim material. The zipper stand uses leather or grosgrain.

**Elastic and Specialized Materials**

Elastic behavior is simulated by reducing weft shrinkage below 100%. At 80% weft shrinkage, the fabric pulls inward horizontally, mimicking the compression of an elastic band.

Use this for cuffs, waistbands, sock tops, and any area where fabric grips the body.

Stiff materials like leather need different simulation settings. Increase bending stiffness. Reduce shrinkage. Leather does not drape like cotton. It holds shape and creates broader, less frequent folds.

**Ties, Laces, and Accessories**

Small details require small patterns with high particle distances for initial placement, then low particle distances for final detail.

Ties and laces can be simulated as narrow strip patterns. Sew one end to the garment, let the other end hang free. Gravity and collision handle the rest.

For elements like zippers, model the zipper teeth as a separate rigid body and attach the fabric panels to its edges using sewing lines.

**Simulation Artifacts and How to Fix Them**

Every simulation produces artifacts. Folds that are too thin and end abruptly. Fabric that stretches across the body showing the anatomy underneath. Sawtoothing along edges due to low resolution.

The first line of defense is going back to the simulation. Adjust the pattern, change the shrinkage, increase the particle distance. Many artifacts disappear with better simulation settings rather than hours of sculpting.

When you export to a sculpting tool, follow this order. First, adjust the silhouette. Move edges, fix proportions, make the garment fit the way your reference shows. Second, remove unwanted folds and visible anatomy. A thick cotton flannel should not show the chest muscles underneath. Smooth those areas. Third, add secondary and tertiary folds that the simulation missed. Seam details, memory folds, micro-wrinkles at stress points.

What you should not do is completely resculpt areas. If the fold structure is fundamentally wrong, go back to the simulation tool and fix it there. Sculpting new folds from scratch looks different from simulated folds, and the inconsistency shows.

**The Concept Analysis Phase**

Before building any complex garment, break it down. Study your reference and answer these questions.

How many panels does this garment have? Where are the seams? What materials are used? How does the fabric behave at each seam? Where does the garment contact the body, and where does it float freely?

Sketch the panel layout. You do not need artistic skill. Rough rectangles and arrows showing how panels connect. This sketch becomes your blueprint in the simulation tool.

Identify the hardest part of the garment. For a puffer jacket, it is the quilted panel structure. For a layered skirt, it is getting the tiers to drape correctly without clipping. Start with the hardest part. If you can solve that, the rest falls into place.

**Building a Fitting Suit**

A fitting suit is a tight bodysuit that sits between your avatar and your garment. Its purpose is to prevent the outer garment from clipping into the body during simulation.

Think of it as a buffer layer. When the outer garment pushes inward, it hits the fitting suit instead of the naked avatar geometry. This produces cleaner folds at contact points and eliminates most body-clipping artifacts.

Build the fitting suit once for your avatar. Save it as part of your avatar file. Load it every time you start a new garment.

### Exercises

- [ ] Identify primary, secondary, and tertiary folds on a reference photo of a real jacket
- [ ] Create two versions of the same shirt: one fitted (95% scale) and one loose (110% scale)
- [ ] Build a collar using a stiffer material preset and sew it to a garment neckline
- [ ] Simulate elastic cuffs by setting weft shrinkage to 75% on sleeve-end panels
- [ ] Add a zipper stand to a jacket front and simulate the opening

---

## Chapter 4: Topology, Retopology, and Game-Ready Meshes

Simulation meshes are beautiful. They are also unusable in a game engine.

A simulated garment might have 500,000 triangles with zero edge flow. Game engines need clean quad meshes with proper topology that subdivides predictably and bakes normals correctly.

This chapter covers the bridge between simulation and production.

**Why Retopology Matters**

Simulation software generates triangulated meshes. The triangle layout is optimized for physics, not for art. When you try to subdivide these triangles in a sculpting tool, you get pinching, distortion, and unpredictable behavior.

Clean quad topology gives you subdivision levels that you can navigate smoothly. You can sculpt broad changes at low subdivisions and fine details at high subdivisions. You can add edge loops where you need them. You can create proper UV layouts.

**Polygon Budgets**

Before you start retopology, know your target.

A game-ready garment for a current-gen console character might use 2,000 to 8,000 polygons per piece. A mobile game might budget 500 to 2,000. A cinematic render has no practical limit.

Your high-poly sculpt should have enough subdivisions to capture all the detail you want to bake into normal maps. Typically, this means 200,000 to 2,000,000 polygons depending on the garment.

Your low-poly retopology is what ships in the game. The normal map carries the illusion of all that high-poly detail on a fraction of the geometry.

**Retopology Methods**

There are three main approaches, from fastest to most controlled.

Automatic remeshing (built into simulation software) converts triangles to quads algorithmically. Fast, but the flow is rarely ideal. Good for roughing out or when you are in a hurry.

Semi-automatic remeshing (ZRemesher in ZBrush) gives better results with some guidance. Set polygroups on your mesh, enable edge detection, and let the algorithm create topology that follows your mesh structure.

Manual retopology (Quad Draw in Maya, RetopoFlow in Blender) gives complete control. You draw quads directly onto the surface of your simulation mesh. Slowest method, best results.

**Topology Flow Principles**

Edge loops should follow the natural contours of the garment. Seams need supporting edge loops on both sides. Panel edges need at least one row of quads running parallel to the edge.

Avoid star poles (vertices where 5+ edges meet) near visible seams or areas you plan to sculpt detail. Place them in flat, low-detail areas where they will not cause visual artifacts.

Quad sizing should be consistent across the mesh. Huge quads next to tiny quads create uneven subdivision detail.

**The Projection Workflow**

After retopology, you need to transfer detail from the high-poly simulation mesh to your clean topology.

In ZBrush, use Project History. Subdivide your clean topology, project the simulation detail, subdivide again, project again. Repeat until the detail matches.

In Maya, use Transfer Attributes. Set the transfer space to UV (since both meshes share the same UV layout from the original patterns). Transfer vertex positions from the simulation mesh to the clean mesh.

This projection workflow is the core bridge between simulation and production. Master it once, use it on every garment.

**Adding Thickness**

Real fabric has thickness. A single-sided polygon surface looks paper-thin from any angle.

Use Panel Loops in ZBrush to extrude edges inward, adding a bevel and thickness in one operation. Set the elevation to negative so the extrusion goes inward (you already have the correct outer surface).

Alternatively, use Extrude in Maya with a small negative offset along normals.

Thickness matters most at edges and seams, where the camera sees the garment's profile. Even a small amount (0.5 to 2mm at real-world scale) makes a visible difference.

**Decimation and Optimization**

For game-ready meshes, you need to reduce polygon count while preserving silhouette and normal map quality.

Decimation removes polygons algorithmically while trying to preserve shape. It produces triangles, not quads, but for a game-ready mesh that will be normal-mapped, this is acceptable.

Preserve hard edges at seams and panel boundaries during decimation. These define where your normal map needs sharp transitions.

### Exercises

- [ ] Export a simulated garment and attempt automatic quadrangulation, then compare to manual retopology
- [ ] Define a polygon budget for a mobile game character (full outfit, head to toe)
- [ ] Retopologize one garment panel using Quad Draw or an equivalent tool, aiming for even quad distribution
- [ ] Project detail from a simulation mesh onto clean topology using subdivision + projection
- [ ] Add thickness to a garment using Panel Loops or Extrude, targeting 1mm at real-world scale

---

## Chapter 5: Texturing, Detailing, and Final Presentation

A beautifully modeled garment with flat gray material is invisible in a portfolio. Texturing, rendering, and presentation are what sell the work.

**UV Layout**

Your simulation software generates UVs from the 2D patterns. These are often usable as-is, but check for overlapping panels and inconsistent texel density.

For game assets, each garment piece should fit within 0 to 1 UV space. If your patterns produce UVs outside this range, adjust them in your 3D package.

Unified UV coordinates ensure that texture resolution is consistent across the entire garment. Check this option when exporting from simulation software.

**Texture Blockout**

Start with flat colors. Assign a base color to each material zone (body, collar, cuffs, zipper) and render to make sure the silhouette and proportions read correctly before investing time in detailed textures.

This stage catches problems early. If the garment does not look good in flat color, adding detail will not fix it.

**Leather, Denim, and Specialty Fabrics**

Each fabric type requires a different texturing approach.

Leather uses a combination of noise patterns at different scales. Large-scale noise for the overall surface variation. Medium-scale for pore structure. Small-scale for grain detail. Add subtle color variation in the diffuse map. Real leather is never one uniform color.

Denim has a visible diagonal weave pattern (the bias). Create the weave as a tiling texture, then add wear patterns at stress points: knees, seat, pocket edges. Faded denim tells a story of use.

Cotton reads through subtle fiber direction and soft, diffused highlights. Keep roughness high (0.7 to 0.9) and use a fabric normal map for surface texture.

**Stitch Maps and Seam Detail**

Stitches are the most common detail that separates good from great.

Create stitch patterns as tiling textures or stamps. A double-needle stitch, a topstitch, a serged edge. Each has a distinct visual signature.

Apply stitches along seam lines using projection in your texturing tool. Vary the stitch spacing and thread color subtly across the garment.

**Fabric Damage and Wear**

New clothing looks fake. Real garments show wear.

Add subtle fuzz along edges where fabric frays. Lighten color at fold peaks where dye wears thin. Add micro-pilling on surfaces that rub against other surfaces.

Fur and fuzz can be painted using strand-based tools or applied as cards (small polygon strips with alpha textures).

**Baking Normal Maps**

The normal map transfers your high-poly sculpt detail to the low-poly game mesh. Set up your high-poly and low-poly in the baking tool. Adjust the cage (the projection distance) to capture all detail without artifacts.

Common baking problems and solutions:

Seam artifacts: add padding/bleed in your bake settings. Hard edges on the low-poly should match UV island boundaries.

Skewing at curved surfaces: increase cage distance or add more geometry to the low-poly in problem areas.

Missing detail: ensure the high-poly and low-poly are properly aligned before baking.

**Posing for Presentation**

A static A-pose tells you nothing about how the garment moves. Pose your character.

Casual standing poses show drape and fit. Walking poses show movement and fold behavior. Seated poses show how fabric bunches at joints.

Your simulation software can re-simulate garments on posed avatars. Export the posed avatar, drape the garment, and render.

For portfolio presentation, use a neutral background, consistent lighting (3-point setup with a soft key light), and multiple angles. Include a wireframe render to show topology quality.

**Rendering for Maximum Impact**

Your render setup matters as much as your modeling. A poorly lit masterpiece looks like amateur work.

Use a three-point lighting setup. A soft key light at 45 degrees illuminates the primary side of the garment. A fill light on the opposite side reduces harsh shadows. A rim light behind the model separates it from the background and highlights the silhouette.

Background should be neutral. Dark gray or light gray depending on the garment color. Never use a busy background that competes with the clothing for attention.

Render at least four angles: front three-quarter, back three-quarter, side profile, and a close-up detail shot. Each angle reveals different aspects of your work. The front shows fit and proportion. The back shows construction and fold behavior. The side shows silhouette. The close-up shows material quality and detail.

Include a wireframe overlay render. Studios hiring character artists want to see your topology. A clean wireframe signals technical competence that even a beautiful render alone does not prove.

**Building a Portfolio That Gets Hired**

Five to ten finished garments across different types. Casual wear, outerwear, formal wear, accessories. Show range.

For each garment, present the process. Reference board, simulation screenshot, sculpting pass, final render. This tells the viewer you understand the pipeline, not just the end result.

Write a brief description for each piece. What software you used, what challenges you solved, what you learned. Art directors read these. They want to know you can think about your work, not just execute it.

Post consistently on ArtStation, LinkedIn, and Twitter. Tag studios you want to work for. Engage with other artists. The digital fashion community is small enough that consistent, quality work gets noticed quickly.

**The Business of Digital Fashion**

Digital clothing is a growing market across multiple platforms.

Game studios need character artists who understand cloth simulation. Film studios need digital wardrobe departments. Virtual fashion brands sell directly to consumers in platforms like Roblox, Fortnite, and VRChat.

Start by building a portfolio of 5 to 10 garments across different types: casual, formal, outerwear, accessories. Show the process, not just the final render. Studios want to see that you understand the pipeline.

Price digital assets based on complexity and platform. Simple game-ready pieces sell for $10 to $50 on asset marketplaces. Custom commissions for game studios range from $200 to $2,000+ per garment depending on detail level.

**UV Space Management for Complex Garments**

When a garment has many panels, fitting everything into a single UV tile (0 to 1 space) requires careful planning. Prioritize visible areas. The front of a jacket should get more UV space (and therefore more texture resolution) than the inner lining that players rarely see.

Use UV packing tools to maximize space utilization. Most 3D packages have automatic packing, but manual adjustments almost always produce tighter, more efficient results.

For game assets with multiple garments on a single character, consider a shared texture atlas. All garments share one material with one set of textures. This reduces draw calls in the game engine, which directly improves frame rate.

**Normal Map Details**

Your normal map is where most of the visible detail lives on a game-ready asset. Bake from your high-poly sculpt to your low-poly retopology.

Padding (also called bleed or dilation) extends the texture data beyond UV island boundaries. Without padding, you see visible seams where UV islands meet. Set padding to at least 4 pixels, ideally 8 or more.

After baking, check for common artifacts. Waviness along curved surfaces indicates the cage projection distance is too small. Dark splotches at corners indicate geometry overlap. Fix these by adjusting the cage or separating geometry before re-baking.

Hand-paint corrections on the normal map when needed. A quick fix with a normal map painting tool can save hours of re-baking.

**File Organization and Naming**

Professional studios expect organized project files. Name everything with a consistent convention. Garment type, material, version number. "jacket_leather_v03.zpr" tells anyone exactly what they are opening.

Keep separate folders for reference, patterns, simulation files, sculpt files, retopology, textures, and final exports. When you return to a project after three months, organization is the difference between a 5-minute pickup and a full-day archaeology session.

### Exercises

- [ ] Export UVs from a simulated garment and verify they fit within 0-1 space with no overlapping
- [ ] Create a texture blockout with flat colors for each material zone on a garment
- [ ] Apply a stitch detail texture along one seam line of a garment
- [ ] Bake a normal map from a high-poly garment onto a low-poly retopologized version
- [ ] Pose a character in at least 3 positions and render the garment from 4 angles each

---

## About the Author

Behike builds digital products and teaches creative technology from Puerto Rico. Follow @behikeai on Instagram for more.
