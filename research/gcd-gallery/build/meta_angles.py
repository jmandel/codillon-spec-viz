ARGON = 'Gemini 4 Argon'
PRO = 'Gemini 3.1 Pro, redrawn for this page'


def A(nn, short, heading, angle, claim, strong, figs, encoding, hides, audit_html, table, model=ARGON, also_html=''):
    return dict(nn=nn, short=short, heading=heading, angle=angle, claim=claim, strong=strong, figs=figs,
                encoding=encoding, hides=hides, audit_html=audit_html, table=table, model=model, also_html=also_html)


TD = 'teaching the definition'
DB = 'debugging a program'
ED = 'inside the editor'

ANGLES = [
    A('02', 'Strips', 'Pins in sockets', 'angle 02 · divisor strips on a number line',
      'Gcd(a, b) is the one number whose row of divisors fills every common-divisor socket exactly: no socket left '
      'empty, no pin spilling outside.',
      5,
      [(1, 'Div(12) and Div(8) agree on sockets 1, 2, 4; only Div(4) fills exactly those, so the type is {4}.'),
       (2, 'g = 2 leaves socket 4 empty, g = 8 spills pin 8, g = 6 does both.'),
       (3, 'Each Euclid step changes both rows but not the sockets {1, 2, 4}; at y = 0 the full row Div(0) changes nothing.'),
       (4, 'Coprime 13, 8 share one socket, {1}; for (0, 0) every d is a socket and only g = 0 fills them all.'),
       (5, '“No spills” gives {1, 2, 4}; “no empty sockets” gives {0, 4, 8, …}; both together give {4}.')],
      [('column', 'a candidate divisor d = 0, 1, 2, …'),
       ('navy pin', 'd divides this row’s number'),
       ('purple socket', 'd is a common divisor of a and b'),
       ('hollow dark-red socket', 'a common divisor the candidate misses'),
       ('crossed dark-red pin', 'a divisor of the candidate that is not common')],
      'A literal number line only works for small numbers, and divisors appear as unrelated dots, so the order '
      'structure behind “greatest” stays implicit.',
      'No wrong numbers. Fixed: a heading claimed all g in 0…12 were tested (7 are drawn); three “↑” pointers sat under '
      'the wrong columns; “0 spills” read as “divisor 0 spills”.',
      dict(drawn='rows of divisor pins against common-divisor sockets',
           error='an empty dark-red socket or a crossed pin',
           dep=('partly', 'sockets recomputed for each pair'),
           loop=('partly', 'socket row unchanged along one run'),
           use=[TD, DB]),
      also_html='The interactive version of this picture is §1 of <a href="gcd-as-a-type.html#s1">gcd-as-a-type</a>.'),

    A('06', 'Predicates', 'Conjuncts as overlapping regions', 'angle 06 · refinement as nested predicate regions',
      'Each conjunct of Gcd(a, b) carves a region out of ℕ; the three regions meet in exactly one number, and dropping '
      'any conjunct lets an impostor in.',
      1,
      [(1, 'Each of the eight compartments holds its own witnesses; only 4 lies in all three regions, as the 0…12 sieve confirms.'),
       (2, 'Adding a conjunct shrinks the set: {4} ⊂ {1, 2, 4} ⊂ Div(12) ⊂ ℕ. Subtyping is containment.'),
       (3, 'Drop one conjunct and an impostor leaks in: 2 without P₃, 8 without P₁, 12 without P₂.'),
       (4, 'Coprime, large, (21, 0) and (0, 0) inputs reshape the regions, yet exactly one value survives.'),
       (5, 'Euclid’s steps (12, 8) → (8, 4) → (4, 0) reshape the outer regions while the common lens {1, 2, 4} stays.')],
      [('solid circle', 'P₁: g ∣ a'),
       ('dashed circle', 'P₂: g ∣ b'),
       ('dotted circle', 'P₃: every common divisor divides g'),
       ('number pill', 'which conjuncts that value satisfies'),
       ('dark-red region or pill', 'a value a weakened spec wrongly admits')],
      'Same-sized circles hide that Div(a) is finite while P₃ and ℕ are infinite, and that P₃ is computed from '
      'P₁ ∩ P₂ rather than being an independent set.',
      'No wrong numbers: all 83 number pills sit in the right compartment (checked against the circle geometry). '
      'Fixed: incomplete pill lists for (1071, 462), a wrong reason for the empty compartment, a garbled leak '
      'sentence, a footer claiming every step only removes divisors, and eight overlaps.',
      dict(drawn='three overlapping predicate regions in ℕ',
           error='a value in a dark-red compartment missing a conjunct',
           dep=('partly', 'regions redrawn for four pairs'),
           loop=('partly', 'common lens fixed along one run'),
           use=[TD])),

    A('01', 'Lattice', 'The top of two cones', 'angle 01 · divisibility lattice',
      'In the divisibility lattice Div(a) and Div(b) are downward cones; Gcd(a, b) is the single node whose own cone '
      'is exactly their overlap.',
      1,
      [(1, 'Div(12) and Div(8) overlap in {1, 2, 4}, which is exactly the cone below 4: the meet 12 ∧ 8.'),
       (2, '2 sits inside the overlap but misses 4; 8 leaves Div(12); 6 strays onto the ×3 branch.'),
       (3, 'Same lattice, different inputs: the overlap and its top move to 4, 6, then 1.'),
       (4, 'd ∣ n is cone containment; 0 sits above every number, so Gcd(12, 0) = {12}.'),
       (5, 'Euclid’s states (12, 8) → (8, 4) → (4, 0) change the cones, never their overlap {1, 2, 4}. '
           '(The outer cones shrink on this run only.)')],
      [('node position', 'prime exponents: up-left ×2, up-right ×3'),
       ('arrow u → v', 'v = u·p, so u ∣ v'),
       ('dashed hull', 'Div(a) or Div(b): everything below the input'),
       ('purple capsule', 'Div(a) ∩ Div(b), the target cone'),
       ('dark-red cone', 'Div(g) of a wrong candidate')],
      'It stays readable for two primes only, a mod step jumps across the lattice instead of following edges, and '
      'fig. 5’s shrinking cones are true of this run, not in general.',
      'No wrong numbers (10 cover edges of Div(24), every hull, every candidate). Fixed: Div(2) drawn in indigo, '
      'the colour reserved for “unknown”; three label collisions; two overflowing text lines.',
      dict(drawn='Hasse diagram; the type is the top of an overlap',
           error='a dark-red cone that is not the purple cone',
           dep=('yes', 'cones move with (a, b)'),
           loop=('partly', 'overlap shown invariant, not derived'),
           use=[TD])),

    A('03', 'Exponent boxes', 'Prime-exponent boxes', 'angle 03 · prime-exponent space',
      'Plot each number by its exponents of 2 and 3: Div(n) becomes the box below n, and Gcd(a, b) is the one corner '
      'whose box is exactly the overlap.',
      1,
      [(1, 'Div(12) and Div(8) are boxes; their overlap {1, 2, 4} has one top-right corner, 4 = 2²·3⁰.'),
       (2, '(72, 48) gives corner 24; coprime (13, 8) collapses to 1; (24, 0) leaves Div(24) unchanged.'),
       (3, 'Wrong answers for (12, 8): the box of 2 misses 4; the boxes of 12 and 8 overflow b and a.'),
       (4, 'Euclid on (72, 48): the outer boxes change each step, the purple overlap stays [0,3]×[0,1].'),
       (5, '1071 and 462 involve five primes: one min-bar per prime gives 3¹·7¹ = 21.')],
      [('grid point (i, j)', 'the number 2ⁱ·3ʲ'),
       ('dashed and dotted boxes', 'Div(a) and Div(b)'),
       ('purple box', 'Div(a) ∩ Div(b): the box below the componentwise min'),
       ('double-ringed corner', 'g, the only inhabitant'),
       ('dark-red box or hatched cell', 'a candidate that overflows or falls short')],
      'It needs factorizations Euclid never computes, a remainder can raise an exponent (1071 mod 462 = 147 = 3·7²), '
      'and 0 has no point, so Div(0) = ℕ is only a drawing convention.',
      'No wrong numbers (all factorizations and box extents read from the SVG). Fixed: “outer box shrinks toward the '
      'corner”, which is false at both steps; “{3, 6, 12} ∤ 8” applied ∤ to a set; three label collisions.',
      dict(drawn='origin-anchored boxes on an exponent grid',
           error='a dark-red box that overflows or falls short',
           dep=('yes', 'overlap box reshapes with (a, b)'),
           loop=('partly', 'overlap fixed, but boxes jump'),
           use=[TD])),

    A('07', 'Ideal', 'The generator of an ideal', 'angle 07 · Bézout / ideal view',
      'The combinations ax + by are exactly the multiples of one number g; Gcd(a, b) = {g}, the step of that lattice '
      'and its first positive point.',
      1,
      [(1, 'Strides 12 and 8 combine into the finer lattice 4ℤ; 12·1 + 8·(−1) = 4 reaches its first positive point.'),
       (2, 'Each (x, y) in ℤ² lands on 12x + 8y; the lines 12x + 8y = 4k collapse onto 4ℤ with empty strips between.'),
       (3, 'Extended Euclid on (1071, 462) ends at 1071·(−3) + 462·7 = 21; coprime (13, 8) reaches every integer.'),
       (4, 'Wrong candidates: grid 8ℤ misses the reachable 4 and 12; grid 2ℤ has unreachable ghosts 2, 6, 10, ….'),
       (5, 'Divisibility mirrors ideal containment; (21, 0) and (0, 0) need no special case.')],
      [('purple dot on ℤ', 'a value ax + by some (x, y) reaches'),
       ('double-ringed dot', 'the generator g'),
       ('shaded box (0, g)', 'the gap no combination lands in'),
       ('navy arc or (x, y) label', 'a Bézout certificate'),
       ('dark-red ✕ or dashed ?', 'off a wrong grid, or unreachable')],
      'It needs signed coefficients in ℤ while the program works in ℕ, and it never shows the divisor sets the type '
      'is defined by.',
      'No wrong numbers (every certificate, all 49 lattice values, all 13 fiber lines). Fixed: the type was written '
      '{g | g > 0 ∧ …}, which excludes Gcd(0, 0) = {0}; “invariant!” labelled a Bézout witness; five overlaps.',
      dict(drawn='lattice aℤ + bℤ = gℤ on the integers',
           error='a dark-red ✕ off the grid, or a ghost',
           dep=('partly', 'one lattice drawn per pair'),
           loop=('partly', 'each step keeps the same ideal'),
           use=[TD])),

    A('08', 'Family', 'A family of singleton fibers', 'angle 08 · dependent type family',
      'Gcd(a, b) is not one set but a family: over each input pair sits the singleton {gcd(a, b)}, and a result must '
      'land in the fiber over its own inputs.',
      2,
      [(1, 'The base plane labelled by gcd; the fiber over (12, 8) keeps only g = 4, since Div(4) = {1, 2, 4}.'),
       (2, 'Fix b = 8 and slide a: the singleton jumps among {8}, {1}, {2}, {4} with period 8.'),
       (3, 'Over (12, 8), returning 8, 2 or 12 is a type error: each inhabits some other pair’s fiber.'),
       (4, 'Euclid’s runs stay on one level set of the plane until y = 0, where Gcd(x, 0) = {x}.'),
       (5, 'An editor gutter tracks the fiber per instruction: return x lands in Gcd(a, b); return y = 0 does not.')],
      [('grid cell (a, b)', 'one index of the family, labelled gcd(a, b)'),
       ('vertical line over an input', 'the ambient return type ℕ'),
       ('purple ring on that line', 'the fiber Gcd(a, b), one element'),
       ('navy dot', 'a returned value'),
       ('dark-red ✕', 'a value that belongs to another pair’s fiber')],
      'Every fiber is a singleton, so “fiber” and “value” blur; the plane’s tints lump several gcds together; the '
      'divisor sets that explain membership live in side panels.',
      'No wrong numbers (all 289 and 484 plane cells, the period-8 slice, both trajectories). Fixed: four labels '
      'that called the wrong thing the fiber (a whole ℕ line, the set Div(x) ∩ Div(y), a column with rejected '
      'values); two overflows.',
      dict(drawn='a singleton over each point of the (a, b) plane',
           error='the result sits in another pair’s fiber',
           dep=('yes', 'it is the subject of the picture'),
           loop=('partly', 'runs stay on one level set'),
           use=[TD])),

    A('04', 'Tiling', 'Euclid’s square tiling', 'angle 04 · Euclid’s rectangle tiling',
      'A common divisor is a square tile that fills the a×b rectangle exactly; cutting y×y squares off keeps every '
      'such tile, down to the largest one, the gcd.',
      2,
      [(1, 'Of square sizes 1–6, only 1, 2 and 4 tile 12×8 without overhang; every valid grid nests in the 4×4 tile.'),
       (2, 'Cutting y×y squares never adds or removes a fitting tile: (12, 8) keeps {1, 2, 4}; (30, 18) keeps {1, 2, 3, 6}.'),
       (3, 'Coprime 13×8 spirals down to 1×1 squares; a 21×0 strip accepts every tile height, so Gcd(21, 0) = {21}.'),
       (4, 'Wrong answers: 8×8 tiles overhang width 12; 2×2 misses the coarser 4×4; a buggy remainder changes the type.'),
       (5, 'States with equal gcd form level sets; each step stays on one; a symbolic cut proves it for unknown (x, y).')],
      [('navy rectangle', 'the pair (a, b) or state (x, y), to scale'),
       ('purple d×d grid', 'a common divisor: it tiles both sides'),
       ('dark-red hatched overhang', 'd does not divide a side'),
       ('dashed cut', 'one Euclid step removing q squares of side y'),
       ('indigo rectangle', '(x, y) unknown at compile time')],
      'Only small inputs fit to scale, a zero side has no area so Div(0) = ℕ is a convention, and “largest tile” can '
      'hide the clause that every common tile nests inside g.',
      'Fixed two wrong statements about 0: “Div(0) = ℕ = {1, 2, 3, …}” and “all d ≥ 1” both left out 0, which divides 0. '
      'Also fixed: Euclid’s cut lines were dark red, the colour reserved for violations, and the halting state 4×0 was '
      'captioned as if it were a 4×4 square.',
      dict(drawn='a rectangle tiled by d×d squares',
           error='tiles overhang the edge, or a coarser tile is missed',
           dep=('yes', 'the rectangle is the index (a, b)'),
           loop=('yes', 'the lemma: cut squares carry the same tiles'),
           use=[TD, DB]),
      also_html='The same lemma with a d-grid you can drag is §2 of <a href="gcd-as-a-type.html#s2">gcd-as-a-type</a>.'),

    A('05', 'State space', 'The loop’s state has a type', 'angle 05 · state-space invariant',
      'The invariant is the set of states (x, y) with gcd(x, y) = gcd(a, b); every Euclid step stays inside it and '
      'moves down, and the exit row meets it in the single cell (g, 0).',
      1,
      [(1, 'All 20 arrows from shaded cells land shaded and point down; the exit row meets the set only at (4, 0).'),
       (2, 'On each ray through the origin the gcd counts 1, 2, 3, …; the set takes the cell with gcd 4 on every ray.'),
       (3, 'Change (a, b) and the set changes: coprime inputs give a dense set, (0, 0) a single point.'),
       (4, 'A true but too-weak invariant (x, y both even) passes entry and preservation and fails exit: 11 exit cells, '
           'only (4, 0) allowed.')],
      [('shaded cell', 'a state (x, y) in the invariant set'),
       ('light arrow', 'one loop step (x, y) → (y, x mod y)'),
       ('navy rings and arrows', 'the actual run'),
       ('exit row y = 0', 'loop exit; its one shaded cell projects to Gcd(a, b)'),
       ('dark-red exit cells', 'results a too-weak invariant would allow')],
      'It shows that the step preserves the set but not why x mod y keeps the common divisors (that is angle 04), '
      'and a grid reaches only small numbers.',
      'The original four figures had correct sets, arrows and runs, but no background, dense arrow fields that hid '
      'the set, a clipped label, a near-empty (0, 0) grid, and the whole too-weak invariant painted dark red. They '
      'were redrawn from the same design and the same computed sets: lighter arrows from shaded cells only, a separate '
      'rays figure, three small multiples, and dark red only on the wrong exit cells.',
      dict(drawn='the set of loop states on an (x, y) grid',
           error='the exit row meets the set in many cells',
           dep=('yes', 'the shaded set is redrawn per pair'),
           loop=('yes', 'closure, descent and one exit cell'),
           use=[DB, TD]),
      model=PRO,
      also_html='The interactive state space, with every successor arrow on a toggle, is §4 of '
                '<a href="gcd-as-a-type.html#s4">gcd-as-a-type</a>.'),

    A('09', 'Derivation', 'The proof as docked tiles', 'angle 09 · typing derivation as composed pictures',
      'Typing Euclid as Gcd(a, b) is a chain of set-to-set judgments joined by containments; the invariant makes every '
      'joint fit, and the last one lands in the singleton {gcd}.',
      3,
      [(1, 'Gcd(12, 8) filters ℕ down to {4}; a judgment is a set-to-set tile, and tiles compose when output ⊆ next input.'),
       (2, 'The loop rule: the step sends every invariant state with y ≠ 0 back into the invariant while y drops 8 > 4 > 0.'),
       (3, 'Four tiles (entry, loop, exit slice y = 0, return) dock to prove Euclid(12, 8) : Gcd(12, 8) = {4}.'),
       (4, 'The same skeleton for (13, 8), (21, 0) and (0, 0): only the invariant set changes, giving {1}, {21}, {0}.'),
       (5, 'Three bugs, three broken joints: an early exit returns 8, a corrupt body leaks (2, 0), return y gives 0.')],
      [('tile', 'one typing judgment: pre-state set in, post-state set out'),
       ('purple dots on the (x, y) grid', 'states satisfying the invariant'),
       ('purple ⊆ pill between tiles', 'output set fits the next input set'),
       ('navy arrows', 'one concrete run'),
       ('dark-red ⊈ joint with ringed state', 'the failing joint and its counterexample')],
      'Each picture checks one input pair on a finite window, so “for every state in the invariant” looks like '
      'inspecting a few dots, and the decreasing measure is shown, not proved.',
      'Three wrong statements fixed, all in fig. 5: an infinite leak set {0, 4, 8, 12, …} was written as four values; '
      'the buggy-body witness was drawn on the correct run, not the buggy one, which goes (12, 8) → (4, 4) → (2, 0); '
      'and Div(0) was written without 0. Also fixed: a false general claim and a window that made Inv(21, 0) look like one point.',
      dict(drawn='a chain of docked set-to-set judgment tiles',
           error='a dark-red ⊈ joint with a leaking state',
           dep=('partly', 'same skeleton, invariant redrawn per pair'),
           loop=('yes', 'entry, preservation, exit, composed'),
           use=[DB, ED]),
      also_html='A five-rule version of this derivation with an in-page checker is '
                '<a href="gcd-foundations.html#s-derivation">gcd-foundations</a>.'),

    A('10', 'Editor', 'The type as a socket', 'angle 10 · Codillon’s editor idiom',
      'Inside Codillon’s stack fractions, Gcd(a, b) is a one-slot socket on the result’s i32 number line, tied to a and '
      'b; the right return value seats, anything else spills over the rim.',
      4,
      [(1, 'Plain i32 boxes widen into number lines; values seat in admitted regions, 0 spills from a divisor cup, Gcd(12, 8) is one socket.'),
       (2, 'Euclid’s loop as refined fractions for (12, 8): 12 rem_u 8 = 4, the common divisors stay {1, 2, 4}, and 4 seats. '
           'The listing is abridged: no local initialization, no block, br or end.'),
       (3, 'Change the inputs and the tied socket moves: 21 for (1071, 462), 1 for (13, 8), 21 for (21, 0), 0 for (0, 0).'),
       (4, 'Returning 2, 8 or 12 instead of 4 misses the socket and spills; each miss traces to a divisor set other than {1, 2, 4}.'),
       (5, '{4} fits every wider type down to plain i32, and at run time sockets and ties erase to plain 12, 8 → 4.')],
      [('cup above the rule / shape below', 'value consumed / value produced'),
       ('wide number line', 'a refined i32 (linear near 0, log toward the ends)'),
       ('shaded band or notch', 'values the refinement admits'),
       ('bold socket tied to a and b', 'Gcd(a, b), its single value'),
       ('dark-red hatch over the rim', 'a value outside its type')],
      'The log wings crush 8, 12, 21, 462 and 1071 into a few pixels; the thin notches beside the socket look admitted '
      'but are not; and the fig. 2 listing is abridged, not a runnable program.',
      'Wrong numbers fixed in fig. 3: Div(462) skipped 6; panel C was titled “zero absorber” (0 is the identity for '
      'gcd); Gcd(0, 0) and Div(0) were shaded over all of i32, negatives included. Also fixed: “;;” starts a WAT '
      'comment, so “i32.const 2 ;; return” hid the return; ties were indigo (the colour for unknown). Not fixable in '
      'place: fig. 2’s listing lacks initialization and block/br/end, so it is labelled abridged.',
      dict(drawn='a one-slot socket on the result’s number line',
           error='the value spills over the cup rim in dark red',
           dep=('yes', 'ties to a and b move the socket'),
           loop=('partly', 'invariant annotated, not drawn'),
           use=[ED, DB]),
      also_html='The real editor idiom these shapes extend is the <a href="00-refined-codillon.html">Refined Codillon walkthrough</a>.'),
]

AUDIT_LOG = dict(
    lead='Before anything went on this page, every figure was audited. Every number and claim in each SVG was '
         'recomputed in Python: divisor sets, gcds, the lattice, Bézout coefficients, tilings, fibers, and invariant '
         'sets checked cell by cell. Each figure was also rendered and checked by eye for overlaps and clipping. As a '
         'final pass, 202 divisor-set, gcd, remainder and Bézout equalities were extracted from all 49 figures and '
         'recomputed; all hold. <b>None of the 49 figures had to be left out.</b> Ten statements were wrong (in angles 02, 04, 09 '
         'and 10), and all ten are fixed. About 35 more misled or broke the colour rules; nearly all are fixed, and '
         'the rest are noted in captions. Angle 05 was redrawn. The source files are untouched; fixes are applied to copies '
         'by scripts.',
    items={
        '01': ['Checked: 10 cover edges of Div(24), node placement, all hulls, Div(18) ∩ Div(12) = {1, 2, 3, 6}, Gcd(9, 8) = {1}, the trace (12, 8) → (8, 4) → (4, 0). No wrong numbers.',
               'PALETTE, fixed: fig. 4 drew Div(2) in indigo, which is reserved for “unknown”; now gray.',
               'LAYOUT, fixed: three label collisions in fig. 2; an overflowing line in fig. 4; an overflowing footer in fig. 5.',
               'MISLEADING, kept and captioned: fig. 5’s outer cones shrink on this run, but not in general; (13, 8) → (8, 5) adds 5.'],
        '02': ['Checked: every pin, socket and cross mapped to its column from SVG coordinates, including 0 ∈ Div(0) and the half-types {1, 2, 4} and {0, 4, 8, 12}.',
               'MATH, fixed: fig. 5’s heading said all g in 0…12 were tested; only {0, 1, 2, 4, 6, 8, 12} are drawn.',
               'MISLEADING, fixed: three “↑” pointers in fig. 2 sat under the wrong columns; “0 spills” and “0 empty” read as “divisor 0”; one set had two names.'],
        '06': ['Checked: all 83 number pills tested against the circle geometry; every compartment; 1071 = 3²·7·17 and 462 = 2·3·7·11. No wrong numbers.',
               'MISLEADING, fixed: incomplete (1071, 462) pill lists without an ellipsis; a wrong reason for the empty compartment; “13, 14, 15, …” as all outside (16 is in P₃); a garbled leak sentence; a footer saying every step only removes divisors.',
               'LAYOUT, fixed: eight pills and labels straddled region edges or overflowed boxes.'],
        '03': ['Checked: factorizations of 12, 8, 72, 48, 24, 104, 1071, 462; box extents and bar heights read from the SVG. No wrong numbers.',
               'MISLEADING, fixed: fig. 4 said twice that the outer box “shrinks toward the corner”, false at both steps.',
               'NIT, fixed: “{3, 6, 12} ∤ 8” applied ∤ to a set. LAYOUT, fixed: three label collisions.',
               'Kept, stated under “what it hides”: Div(0) = ℕ is drawn as a box over the positive integers only.'],
        '07': ['Checked: every certificate a·x + b·y, all 49 lattice values, all 13 fiber lines, the extended-Euclid table for (1071, 462), the 19 witnesses for (13, 8). No wrong numbers.',
               'MISLEADING, fixed: the type was written {g | g > 0 ∧ 12ℤ + 8ℤ = gℤ}, contradicting Gcd(0, 0) = {0}; “(invariant!)” labelled a Bézout witness; “+24 k = +6” read as 24k.',
               'LAYOUT, fixed: five labels struck through by boxes or arrows.'],
        '08': ['Checked: all 289 cells of the (a, b) plane and all 484 of the (x, y) plane against gcd; the period-8 slice; both trajectories. No wrong numbers.',
               'MISLEADING, fixed: four labels called the wrong object the fiber (a line ℕ, the set Div(x) ∩ Div(y), a column with rejected values, “purple cells”).',
               'LAYOUT, fixed: two overflows. Kept: the crosshair strikes through row 8 and column 12 of fig. 1.'],
        '04': ['Checked: every tiling, overhang and quotient; every rectangle is to scale (12×8, 30×18, 13×8, 8×3, 21×0); the gcd = 3 and gcd = 4 point sets of fig. 5.',
               'MATH, fixed: “Div(0) = ℕ = {1, 2, 3, …}” (fig. 3) and “all d ≥ 1” (fig. 2) left out 0, which divides 0.',
               'PALETTE, fixed: Euclid’s cut lines were dark red, which is reserved for violations; now ink.',
               'MISLEADING, fixed: the halting state was captioned as a 4×4 square (it is 4×0); “the fiber’s unique inhabitant” should be the type’s.'],
        '05': ['Checked: every shaded set in the four original figures equals {(x, y) | gcd(x, y) = g} (21, 161, 1 and 121 cells); all arrows land shaded and go down; each primitive ray meets the set once.',
               'LAYOUT: no background, dense arrow fields hiding the set, a clipped label (“ingle exit cell”), a near-empty (0, 0) grid.',
               'PALETTE / MISLEADING: the entire too-weak invariant, including the correct exit (4, 0), was dark red; its text omitted (0, 0).',
               'Redrawn for this page from the agent’s own design and data; every count in the new figures is computed and asserted.'],
        '09': ['Checked: every invariant grid cell by cell against {gcd(x, y) = gcd(a, b)}; all run arrows; the loop step on Inv.',
               'MATH, fixed: the leak set {x | Inv ∧ y ≤ 4} is every multiple of 4, not {0, 4, 8, 12}; bug 2’s witness was drawn on the correct run, not the buggy (12, 8) → (4, 4) → (2, 0); Div(0) was written without 0.',
               'MISLEADING, fixed: a general claim false for (4, 8); Inv(21, 0) drawn on a window that hides all but one point (now labelled “y ≤ 7 shown”).',
               'LAYOUT, fixed: one overflowing line.'],
        '10': ['Checked: the WAT loop simulated for (12, 8), (1071, 462), (13, 8), (21, 0), (0, 0), every local.get/set, eqz and br_if; i32.rem_u operand order; every bead and socket on the log-linear scale.',
               'MATH, fixed: Div(462) skipped 6; “zero absorber” (0 is the identity for gcd); Gcd(0, 0) shaded over all of i32; Div(0) shaded over negatives.',
               'MISLEADING, fixed: “;;” starts a WAT comment, hiding the second instruction; the coprime trace stopped before 2 mod 1 = 0; the 21 socket read as 8; interval shading admitted 3 and 5–11.',
               'PALETTE, fixed: ties and labels were indigo (reserved for unknown); now purple.',
               'Not fixable in place: fig. 2’s listing has no local initialization and no block, br or end. It is labelled abridged here.'],
    })

RECOMMEND = dict(
    lead='No single picture does everything. The table splits the angles into three jobs. Two or three angles cover each '
         'job well:',
    cards=[
        dict(where='Teaching the definition', pick='02 strips, then 08 family',
             why='The divisor strip is the definition read literally. Div(g) and Div(a) ∩ Div(b) sit as two rows, '
                 'and both ways to fail are visible: an empty socket (too small) and a spilled pin (not common). It '
                 'needs no factoring and no ℤ. Follow it with 08 fig. 2 to show that “dependent” means a different '
                 'singleton for every input. Use 01 or 03 for students who already think in prime factors.'),
        dict(where='Explaining why Euclid is correct', pick='04 tiling + 05 state space',
             why='The tiling is the only picture that shows <i>why</i> a step keeps the common divisors, and it does so '
                 'without algebra. The state space is the only one that shows the whole loop obligation at once: '
                 'every arrow stays shaded, every arrow goes down, one exit cell. Together they are the proof. '
                 '09’s docked tiles are the better choice once students must find <i>which</i> obligation a bug broke.'),
        dict(where='Inside the editor', pick='10 socket, opening to 02 and 09',
             why='Only 10 fits Codillon’s per-instruction fractions as they are. The result is a socket tied to its '
                 'parameters, and a wrong return spills. Hovering the socket can open the 02 strip as evidence, and '
                 'a failing obligation between instructions is 09’s broken ⊈ joint with its witness state.'),
    ],
    tail='The others are worth keeping as alternates. 06 is the clearest picture of “refinement = conjunction = '
         'intersection”. 07 suits readers who know Bézout. 01 and 03 make “greatest” mean “top”, not “largest”, at '
         'the price of factoring.')
