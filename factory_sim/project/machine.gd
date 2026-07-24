extends Area2D

signal state_changed(new_state_string)
signal box_produced
signal scrap_produced           
signal temperature_changed(temp) 

enum State { IDLE, PROCESSING, FAULT }
var current_state: State = State.IDLE

var box_queue: Array[Area2D] = []
var current_box: Area2D = null

@onready var color_rect: ColorRect = $ColorRect
@onready var timer: Timer = $ProcessTimer


var temperature: float = 20.0
var last_broadcast_temp: int = 20

func _ready() -> void:
	area_entered.connect(_on_area_entered)
	timer.timeout.connect(_on_process_complete)
	update_visuals()
	
	


func _process(delta: float) -> void:
	
	if current_state == State.PROCESSING:
		temperature += 10.0 * delta
	else:
		temperature -= 15.0 * delta
		
	temperature = clamp(temperature, 20.0, 100.0)
	
	if temperature >= 90.0 and current_state != State.FAULT:
		print("Machine OVERHEATED!")
		break_down()
		
	if int(temperature) != last_broadcast_temp:
		last_broadcast_temp = int(temperature)
		temperature_changed.emit(last_broadcast_temp)

func _on_area_entered(area: Area2D) -> void:
	if area.has_method("stop"):
		area.stop()
		box_queue.append(area)
		process_next_box()

func process_next_box() -> void:
	if current_state == State.IDLE and box_queue.size() > 0:
		current_box = box_queue[0]
		current_state = State.PROCESSING
		update_visuals()
		timer.start(2.0)

func _on_process_complete() -> void:
	if current_box and current_state == State.PROCESSING:
		
		if randf() < 0.2:
			scrap_produced.emit()
			current_box.queue_free() 
		else:
			box_produced.emit()
			current_box.start()
			
		box_queue.pop_front()
		current_box = null
		current_state = State.IDLE
		update_visuals()
		process_next_box()

func break_down() -> void:
	current_state = State.FAULT
	if not timer.is_stopped():
		timer.paused = true
	update_visuals()
	print("Machine FAULT triggered!")

func fix() -> void:
	if current_state == State.FAULT:
		
		if temperature > 60.0:
			print("Too hot to fix! Let it cool down to 80...")
			return
		
		print("Machine FIXED!")
		if current_box:
			current_state = State.PROCESSING
			if timer.paused:
				timer.paused = false
			else:
				timer.start(2.0)
		else:
			current_state = State.IDLE
			process_next_box()
		update_visuals()

func update_visuals() -> void:
	var state_str = ""
	match current_state:
		State.IDLE:
			color_rect.color = Color.DIM_GRAY
			state_str = "IDLE"
		State.PROCESSING:
			color_rect.color = Color.YELLOW
			state_str = "PROCESSING"
		State.FAULT:
			color_rect.color = Color.RED
			state_str = "FAULT"
			
	state_changed.emit(state_str)
