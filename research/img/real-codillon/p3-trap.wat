(func $main
i32.const 12
i32.const 8
call $gcd
drop
)
(func $gcd (param $a i32) (param $b i32) (result i32)
(local $t i32)
block $done
loop $step
local.get $a
i32.eqz
br_if $done
local.get $a
local.get $b
i32.rem_u
local.set $t
local.get $b
local.set $a
local.get $t
local.set $b
br $step
end
end
local.get $a
)
