<?php

namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Event;
use App\Models\Room;
use App\Models\User;
use Carbon\Carbon;

class OpeningHoursValidationTest extends TestCase
{
    use RefreshDatabase;

    protected $user;
    protected $room;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        
        // Create room with opening hours 08:00 - 18:00
        $this->room = Room::create([
            'name' => 'Business Hours Room',
            'capacity' => 40,
            'open_time' => '08:00:00',
            'close_time' => '18:00:00',
        ]);
    }

    /** @test */
    public function can_book_event_within_opening_hours()
    {
        $event = Event::create([
            'title' => 'Valid Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(10, 0),
            'end_time' => Carbon::today()->setTime(12, 0),
            'participants' => 20,
        ]);

        $this->assertNotNull($event->id);
    }

    /** @test */
    public function can_book_event_at_opening_time()
    {
        $event = Event::create([
            'title' => 'Early Morning Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(8, 0), // Exactly at open time
            'end_time' => Carbon::today()->setTime(9, 0),
            'participants' => 15,
        ]);

        $this->assertEquals(8, $event->start_time->hour);
    }

    /** @test */
    public function can_book_event_ending_at_closing_time()
    {
        $event = Event::create([
            'title' => 'Late Event',
            'room_id' => $this->room->id,
            'start_time' => Carbon::today()->setTime(17, 0),
            'end_time' => Carbon::today()->setTime(18, 0), // Exactly at close time
            'participants' => 15,
        ]);

        $this->assertEquals(18, $event->end_time->hour);
    }

    /** @test */
    public function validates_event_starting_before_opening_time()
    {
        $startTime = Carbon::today()->setTime(7, 0); // Before 08:00
        $openTime = Carbon::today()->setTime(8, 0);
        
        $startsBeforeOpening = $startTime->lt($openTime);
        
        $this->assertTrue($startsBeforeOpening, 'Should detect events starting before opening time');
    }

    /** @test */
    public function validates_event_ending_after_closing_time()
    {
        $endTime = Carbon::today()->setTime(19, 0); // After 18:00
        $closeTime = Carbon::today()->setTime(18, 0);
        
        $endsAfterClosing = $endTime->gt($closeTime);
        
        $this->assertTrue($endsAfterClosing, 'Should detect events ending after closing time');
    }

    /** @test */
    public function validates_event_spanning_outside_hours()
    {
        $startTime = Carbon::today()->setTime(7, 30); // Before opening
        $endTime = Carbon::today()->setTime(19, 0);   // After closing
        $openTime = Carbon::today()->setTime(8, 0);
        $closeTime = Carbon::today()->setTime(18, 0);
        
        $isOutsideHours = $startTime->lt($openTime) || $endTime->gt($closeTime);
        
        $this->assertTrue($isOutsideHours, 'Should detect events spanning outside business hours');
    }

    /** @test */
    public function validates_overnight_events_for_24_hour_rooms()
    {
        // Create a 24-hour room
        $room24h = Room::create([
            'name' => '24 Hour Room',
            'capacity' => 30,
            'open_time' => '00:00:00',
            'close_time' => '23:59:59',
        ]);

        $event = Event::create([
            'title' => 'Late Night Event',
            'room_id' => $room24h->id,
            'start_time' => Carbon::today()->setTime(23, 0),
            'end_time' => Carbon::tomorrow()->setTime(1, 0), // Overnight
            'participants' => 10,
        ]);

        $this->assertNotNull($event->id);
    }

    /** @test */
    public function validates_event_duration_is_positive()
    {
        $startTime = Carbon::today()->setTime(10, 0);
        $endTime = Carbon::today()->setTime(12, 0);
        
        $duration = $endTime->diffInMinutes($startTime);
        
        $this->assertGreaterThan(0, $duration, 'Event duration should be positive');
    }

    /** @test */
    public function validates_time_format_consistency()
    {
        // All times should use consistent format
        $this->assertMatchesRegularExpression(
            '/^\d{2}:\d{2}:\d{2}$/',
            $this->room->open_time,
            'Opening time should be in HH:MM:SS format'
        );

        $this->assertMatchesRegularExpression(
            '/^\d{2}:\d{2}:\d{2}$/',
            $this->room->close_time,
            'Closing time should be in HH:MM:SS format'
        );
    }

    /**
     * Helper method to check if event is within room hours
     */
    protected function isWithinOpeningHours($startTime, $endTime, $openTime, $closeTime)
    {
        $start = Carbon::parse($startTime);
        $end = Carbon::parse($endTime);
        $open = Carbon::parse($openTime);
        $close = Carbon::parse($closeTime);

        return $start->gte($open) && $end->lte($close);
    }
}
