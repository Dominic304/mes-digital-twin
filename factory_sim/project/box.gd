extends Area2D

@export var speed: float = 120.0
var is_moving: bool = true
var is_machine_controlled: bool = false

func _process(delta: float) -> void:
	if not is_machine_controlled:
		is_moving = true 
		for area in get_overlapping_areas():
			if area.has_method("stop") and area != self:
				if area.position.x > position.x and not area.is_moving:
					is_moving = false

	if is_moving:
		position.x += speed * delta
	
	if position.x > 1200:
		queue_free()
func stop() -> void:
	is_machine_controlled = true
	is_moving = false
func start() -> void:
	is_machine_controlled = false
	is_moving = true
