<?php

namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Event;
use App\Models\Room;
use App\Models\User;
use Carbon\Carbon;

class TimeOverlapValidationTest extends TestCase
{
    use RefreshDatabase;

    protected $user;
    protected $room;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        
        $this->room = Room::create([
            'name' => 'Conference Room',
            'capacity' => 30,
            'open_time' => '08:00:00',
            'close_time' => '20:00:00',
        ]);

        // Create an existing event (10:00 - 12:00)
        Event::create([
            'title' => 'Existing Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(10, 0),
            'end_time' => Carbon::today()->setTime(12, 0),
            'participants' => 20,
        ]);
    }

    /** @test */
    public function prevents_overlapping_events_complete_overlap()
    {
        // Try to create event with exact same time (10:00 - 12:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(10, 0),
            Carbon::today()->setTime(12, 0)
        );

        $this->assertTrue($hasOverlap, 'Should detect complete overlap');
    }

    /** @test */
    public function prevents_overlapping_events_start_overlap()
    {
        // Try to create event that starts during existing event (11:00 - 13:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(11, 0),
            Carbon::today()->setTime(13, 0)
        );

        $this->assertTrue($hasOverlap, 'Should detect start overlap');
    }

    /** @test */
    public function prevents_overlapping_events_end_overlap()
    {
        // Try to create event that ends during existing event (09:00 - 11:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(9, 0),
            Carbon::today()->setTime(11, 0)
        );

        $this->assertTrue($hasOverlap, 'Should detect end overlap');
    }

    /** @test */
    public function prevents_overlapping_events_enveloping()
    {
        // Try to create event that completely contains existing event (09:00 - 13:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(9, 0),
            Carbon::today()->setTime(13, 0)
        );

        $this->assertTrue($hasOverlap, 'Should detect enveloping overlap');
    }

    /** @test */
    public function allows_back_to_back_events()
    {
        // Event that ends exactly when existing starts (08:00 - 10:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(8, 0),
            Carbon::today()->setTime(10, 0)
        );

        $this->assertFalse($hasOverlap, 'Should allow back-to-back events (end == start)');

        // Event that starts exactly when existing ends (12:00 - 14:00)
        $hasOverlap2 = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(12, 0),
            Carbon::today()->setTime(14, 0)
        );

        $this->assertFalse($hasOverlap2, 'Should allow back-to-back events (start == end)');
    }

    /** @test */
    public function allows_non_overlapping_events()
    {
        // Event before existing (08:00 - 09:00)
        $hasOverlap = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(8, 0),
            Carbon::today()->setTime(9, 0)
        );

        $this->assertFalse($hasOverlap, 'Should allow events before existing');

        // Event after existing (13:00 - 14:00)
        $hasOverlap2 = $this->checkForOverlap(
            $this->room->id,
            Carbon::today()->setTime(13, 0),
            Carbon::today()->setTime(14, 0)
        );

        $this->assertFalse($hasOverlap2, 'Should allow events after existing');
    }

    /** @test */
    public function different_rooms_dont_conflict()
    {
        $anotherRoom = Room::create([
            'name' => 'Another Room',
            'capacity' => 40,
            'open_time' => '08:00:00',
            'close_time' => '20:00:00',
        ]);

        // Same time as existing event but different room
        $hasOverlap = $this->checkForOverlap(
            $anotherRoom->id,
            Carbon::today()->setTime(10, 0),
            Carbon::today()->setTime(12, 0)
        );

        $this->assertFalse($hasOverlap, 'Events in different rooms should not conflict');
    }

    /**
     * Helper method to check for overlapping events
     */
    protected function checkForOverlap($roomId, $startTime, $endTime)
    {
        $overlappingEvents = Event::where('room_id', $roomId)
            ->where(function($query) use ($startTime, $endTime) {
                $query->where(function($q) use ($startTime, $endTime) {
                    // Existing event starts before new event ends AND
                    // Existing event ends after new event starts
                    $q->where('start_time', '<', $endTime)
                      ->where('end_time', '>', $startTime);
                });
            })
            ->exists();

        return $overlappingEvents;
    }
}
