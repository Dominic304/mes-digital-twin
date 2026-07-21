extends Node2D

func _ready():
	print("Hello from Godot! Factory Simulation Initialized.")

	# We will eventually use this to talk to Python
	var test_string = "Godot says: Machine is RUNNING"
	print("Test state to send later: ", test_string)
