# 🎯 Focus Routine Rules - Quick Reference

## When Focus Routines Are Added (5 min max)

### ✅ Rule 1: First Task of the Day
**Always** add a focus routine before the first task
- No prior tasks exist
- Helps you transition from rest to work mode

### ✅ Rule 2: 4+ Hour Gaps
Add focus routine when gap ≥ 4 hours between:
- **Previous task END time**
- **Next task START time**

**Example:**
```
Task A: 10:00 AM - 12:00 PM (ends at noon)
Task B: 4:00 PM - 5:00 PM (starts at 4pm)
Gap = 4 hours ✓ → Focus routine added
```

### ❌ When Focus Routines Are Skipped
- Gap < 4 hours between tasks
- Assumes you're in continuous work mode

**Example:**
```
Task A: 12:00 PM - 12:50 PM (ends at 12:50)
Task B: 4:00 PM - 4:30 PM (starts at 4:00)
Gap = 3.17 hours ✗ → No focus routine
```

## 📊 Gap Calculation Formula

```
Gap Duration = Next_Task_Start_Time - Previous_Task_End_Time
```

**NOT** calculated from current time!

## ⏱️ Focus Routine Constraints

1. **Maximum duration**: 5 minutes
2. **Minimum time needed**: 6 minutes before task starts
3. **Buffer**: 1 minute before task begins
4. **Structure**: 2-3 quick steps

## 🔍 Debug Output

When you run the script, you'll see:

```
Gap Analysis:
  Previous task ended: 12:50 PM
  Next task starts: 04:00 PM
  Gap duration: 190.0 minutes (3.2 hours)

FOCUS ROUTINE DECISION:
================================================================================
✗ Gap between tasks: 3.2 hours (< 4 hours)
✗ Focus routine will be SKIPPED (Rule: Only add for 4+ hour gaps)
================================================================================
```

## 📝 Examples

### Example 1: Morning Start ✅
```
9:00 AM - First meeting
Result: Focus routine added (First task rule)
```

### Example 2: Short Break ❌
```
9:00 AM - 10:00 AM Task 1
10:30 AM - 11:30 AM Task 2 (30 min gap)
Result: No focus routine (< 4 hours)
```

### Example 3: Lunch Break ❌
```
9:00 AM - 12:00 PM Morning session
1:00 PM - 5:00 PM Afternoon session (1 hour gap)
Result: No focus routine (< 4 hours)
```

### Example 4: Long Break ✅
```
9:00 AM - 12:00 PM Morning session
5:00 PM - 7:00 PM Evening session (5 hour gap)
Result: Focus routine added (>= 4 hours)
```

### Example 5: After Lunch ❌
```
12:00 PM - 12:50 PM Lunch meeting
4:00 PM - 5:00 PM Afternoon task (3.17 hour gap)
Result: No focus routine (< 4 hours)
```

### Example 6: Extended Break ✅
```
12:00 PM - 1:00 PM Lunch
6:00 PM - 7:00 PM Dinner meeting (5 hour gap)
Result: Focus routine added (>= 4 hours)
```

## 🎨 Visual Timeline Display

In the timeline viewer:
- **Yellow banner** = Focus routine included
- **Blue banner** = Focus routine skipped
- Banner shows the exact reason and gap duration

## 💡 Why This Logic?

1. **First task**: You need to transition into work mode
2. **4+ hour gaps**: Long enough that you've likely:
   - Left your workspace
   - Done other activities
   - Lost your work "flow"
   - Need to refocus

3. **< 4 hour gaps**: You're likely still:
   - In work mode
   - At your desk
   - In the flow state
   - Don't need a reset

## ⚙️ Customization

To change the 4-hour threshold, edit this line in the code:
```python
elif time_since_last_task and time_since_last_task >= 240:  # 240 minutes = 4 hours
```

Change `240` to:
- `180` for 3 hours
- `300` for 5 hours
- etc.
