# The mining loop

A skeleton, not a finished system. It exists so the drill → powder → blast →
pick cycle can be played end to end, and so the interesting part — what the
blast actually opens up — has one clearly marked place to be replaced.

## The cycle

```
buy powder at Maw Camp  ──►  drill a round in a marked face  ──►  charge the holes
        ▲                                                              │
        │                                                              ▼
   sell the ore  ◄──  pick the exposed ore  ◄──  get clear and fire the round
```

Four faces are chalked up around the route, one per working:

| Face | Where | Grade | Value each | Nodes exposed |
| --- | --- | --- | --- | --- |
| Crooked Rail seam | drift rib, z ≈ 7 | COPPER | 30 cr | 5 |
| Shaft wall | past the Blackshaft deck, z ≈ −16 | IRON | 38 cr | 6 |
| Saint Glimmer | Drowned Pocket exit, z ≈ −37 | GLIMMER | 62 cr | 8 |
| Powderworks face | z ≈ −45 | IRON | 38 cr | 6 |

A round is three holes and three sticks. You start with 60 credits and exactly
three sticks, so the first face is free and teaches the loop; every face after
it has to be paid for out of the last one. Copper is close to break-even
(150 cr of ore for 135 cr of powder), Glimmer pays for four more rounds.

## Controls

| | Desktop | Mobile |
| --- | --- | --- |
| Choose tool | `1` drill · `2` charge · `3` pick | TOOL cycles |
| Use tool | hold `E` | hold USE |
| Fire the round | `B` | BLAST |
| Lantern | `F` | LAMP |
| Debug fly | `G`, then `1`–`9` for viewpoints | — |

Drilling and picking are held actions with a progress bar; charging and
trading are single presses. The prompt above the tool bar always names the
action the current tool can perform on whatever is under the reticle, and says
why when it cannot.

## Firing

`B` lights a five-second fuse on every charged face at once. Anyone still
within 13 m of a charged face when it goes wakes up at Maw Camp. The blast
removes the chalked face, cuts a hole in the rock shell, and calls
`generateBlastResult` for each face that fired.

## Where the procedural generation goes

Two functions, both marked `EXTENSION POINT` in `src/main.js`:

**`carveShell(worldBox)`** removes any part of the tunnel shell that falls
inside a world-space box. Call it with whatever volume the new working
occupies. It is safe to call repeatedly; every breach so far is re-applied
each time, so the shell can be opened up over and over.

**`generateBlastResult(face)`** owns everything the blast leaves behind. The
current body is a placeholder: one rectangular alcove 3.4 m deep, a muck pile
at its mouth, and a fixed number of ore nodes on the back wall. Replace the
whole body. The contract it has to keep is:

- call `carveShell` with the volume it opens,
- add its own colliders with `colliderBox`, remove the rib colliders it has
  made redundant (they carry `userData.rib = { index, sign }` naming the route
  station and which side of the drift they are), and call `rebuildCollision()`
  when it is done,
- put everything it draws under the `dynamic` group, which is never merged
  into the static buffers,
- register each minable thing with `addInteractable(mesh, 'ore', face)` and
  push it onto `face.oreNodes`; the pick handles the rest, and the face is
  marked worked out when that array empties.

Useful things it already has to work with: `face.station` (the route station
at the face, with `p`, `tangent`, `side`, `width`, `height`), `face.out` (the
unit normal pointing into the rock), `face.origin` (floor level at the face),
`face.yaw` (so a group can be oriented with face-local +Z running into the
rock), and `face.grade` / `face.value` for what the deposit is worth.

## Known limitations

- The placeholder alcove is a plain box. That is deliberate — it is the part
  being replaced — but it means blasting two adjacent faces would produce two
  overlapping boxes rather than one merged void.
- Ore nodes are individually drawn, so a very large generated deposit would
  cost draw calls. Anything above about fifty nodes should be batched.
- The economy has no sink beyond powder, so credits accumulate once all four
  faces are worked out.
- Nothing is saved: reloading resets the mine to intact.
