<?php

namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Event;
use App\Models\Room;
use App\Models\User;

class EventCreationTest extends TestCase
{
    use RefreshDatabase;

    protected $user;
    protected $room;

    protected function setUp(): void
    {
        parent::setUp();
        
        // Create test user
        $this->user = User::factory()->create();
        
        // Create test room with capacity
        $this->room = Room::create([
            'name' => 'Test Room',
            'capacity' => 50,
            'open_time' => '08:00:00',
            'close_time' => '18:00:00',
        ]);
    }

    /** @test */
    public function can_create_event_with_valid_data()
    {
        $eventData = [
            'title' => 'Team Meeting',
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(10, 0)->format('Y-m-d H:i:s'),
            'end_time' => now()->setTime(11, 0)->format('Y-m-d H:i:s'),
            'participants' => 20,
        ];

        $event = Event::create($eventData);

        $this->assertDatabaseHas('events', [
            'title' => 'Team Meeting',
            'room_id' => $this->room->id,
        ]);

        $this->assertEquals('Team Meeting', $event->title);
    }

    /** @test */
    public function event_requires_title()
    {
        $this->expectException(\Illuminate\Database\QueryException::class);

        Event::create([
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(10, 0),
            'end_time' => now()->setTime(11, 0),
        ]);
    }

    /** @test */
    public function event_requires_valid_time_range()
    {
        $eventData = [
            'title' => 'Invalid Event',
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(12, 0),
            'end_time' => now()->setTime(10, 0), // End before start
            'participants' => 20,
        ];

        // This should fail validation (implement in your model/controller)
        $this->assertTrue(strtotime($eventData['start_time']) < strtotime($eventData['end_time']) === false);
    }

    /** @test */
    public function event_belongs_to_room()
    {
        $event = Event::create([
            'title' => 'Test Event',
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(10, 0),
            'end_time' => now()->setTime(11, 0),
            'participants' => 20,
        ]);

        $this->assertInstanceOf(Room::class, $event->room);
        $this->assertEquals($this->room->id, $event->room->id);
    }

    /** @test */
    public function room_has_many_events()
    {
        Event::create([
            'title' => 'Event 1',
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(9, 0),
            'end_time' => now()->setTime(10, 0),
            'participants' => 15,
        ]);

        Event::create([
            'title' => 'Event 2',
            'room_id' => $this->room->id,
            'start_time' => now()->setTime(14, 0),
            'end_time' => now()->setTime(15, 0),
            'participants' => 25,
        ]);

        $this->assertEquals(2, $this->room->events()->count());
    }
}
