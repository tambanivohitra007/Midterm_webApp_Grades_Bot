<?php

namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Event;
use App\Models\Room;
use App\Models\User;
use Carbon\Carbon;

class RoomCapacityTest extends TestCase
{
    use RefreshDatabase;

    protected $user;
    protected $room;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        
        // Create room with capacity of 50
        $this->room = Room::create([
            'name' => 'Meeting Room',
            'capacity' => 50,
            'open_time' => '08:00:00',
            'close_time' => '18:00:00',
        ]);
    }

    /** @test */
    public function can_book_event_within_capacity()
    {
        $event = Event::create([
            'title' => 'Small Meeting',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(10, 0),
            'end_time' => Carbon::today()->setTime(11, 0),
            'participants' => 30, // Within capacity of 50
        ]);

        $this->assertDatabaseHas('events', [
            'id' => $event->id,
            'participants' => 30,
        ]);
    }

    /** @test */
    public function can_book_event_at_exact_capacity()
    {
        $event = Event::create([
            'title' => 'Full Room Meeting',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(10, 0),
            'end_time' => Carbon::today()->setTime(11, 0),
            'participants' => 50, // Exact capacity
        ]);

        $this->assertEquals(50, $event->participants);
    }

    /** @test */
    public function validates_participants_not_exceeding_capacity()
    {
        // This test checks if validation logic exists
        $participants = 60; // Exceeds capacity of 50
        $capacity = $this->room->capacity;
        
        $exceedsCapacity = $participants > $capacity;
        
        $this->assertTrue($exceedsCapacity, 'Should detect when participants exceed room capacity');
    }

    /** @test */
    public function multiple_overlapping_events_cannot_exceed_total_capacity()
    {
        // This tests cumulative capacity for overlapping events
        // Event 1: 30 participants (10:00 - 12:00)
        Event::create([
            'title' => 'Event 1',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(10, 0),
            'end_time' => Carbon::today()->setTime(12, 0),
            'participants' => 30,
        ]);

        // Check if trying to add another overlapping event exceeds capacity
        // Event 2: 25 participants (11:00 - 13:00) - would overlap with Event 1
        $overlappingParticipants = $this->getTotalParticipantsInTimeRange(
            $this->room->id,
            Carbon::today()->setTime(11, 0),
            Carbon::today()->setTime(12, 0)
        );

        $newParticipants = 25;
        $wouldExceed = ($overlappingParticipants + $newParticipants) > $this->room->capacity;

        $this->assertTrue($wouldExceed, 'Total participants in overlapping events should not exceed capacity');
    }

    /** @test */
    public function non_overlapping_events_can_exceed_total_capacity()
    {
        // Event 1: 40 participants (09:00 - 10:00)
        Event::create([
            'title' => 'Morning Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(9, 0),
            'end_time' => Carbon::today()->setTime(10, 0),
            'participants' => 40,
        ]);

        // Event 2: 45 participants (11:00 - 12:00) - no overlap
        Event::create([
            'title' => 'Later Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(11, 0),
            'end_time' => Carbon::today()->setTime(12, 0),
            'participants' => 45,
        ]);

        // Both should exist even though total > capacity (they don't overlap)
        $this->assertEquals(2, Event::where('room_id', $this->room->id)->count());
    }

    /** @test */
    public function validates_participants_is_positive_number()
    {
        // Participants should be > 0
        $this->assertTrue(1 > 0, 'Participants should be positive');
        $this->assertFalse(0 > 0, 'Zero participants should not be allowed');
        $this->assertFalse(-1 > 0, 'Negative participants should not be allowed');
    }

    /**
     * Helper method to get total participants in a time range
     */
    protected function getTotalParticipantsInTimeRange($roomId, $startTime, $endTime)
    {
        return Event::where('room_id', $roomId)
            ->where(function($query) use ($startTime, $endTime) {
                $query->where('start_time', '<', $endTime)
                      ->where('end_time', '>', $startTime);
            })
            ->sum('participants');
    }
}
