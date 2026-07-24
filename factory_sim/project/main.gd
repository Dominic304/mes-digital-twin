extends Node2D

@export var box_scene: PackedScene = preload("res://box.tscn")
@onready var machine: Area2D = $Machine
@onready var spawn_timer: Timer = $SpawnTimer

var udp := PacketPeerUDP.new()

func _ready() -> void:
	print("Factory Simulation Running!")
	udp.connect_to_host("127.0.0.1", 5005)
	machine.state_changed.connect(_on_machine_state_changed)
	machine.box_produced.connect(_on_machine_box_produced)
	spawn_timer.timeout.connect(_on_spawn_timer_timeout)

func _on_machine_state_changed(state_str: String) -> void:
	var msg = '{"event": "state", "value": "%s"}' % state_str
	udp.put_packet(msg.to_utf8_buffer())

func _on_machine_box_produced() -> void:
	var msg = '{"event": "produced", "value": 1}'
	print("Attempting to send box produced network packet...")
	udp.put_packet(msg.to_utf8_buffer())

func _on_spawn_timer_timeout() -> void:
	if box_scene:
		var new_box = box_scene.instantiate()
		new_box.position = Vector2(-50, machine.position.y)
		add_child(new_box)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_B:
			machine.break_down()
		elif event.keycode == KEY_F:
			machine.fix()
