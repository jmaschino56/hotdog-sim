import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import math

# Page config
st.set_page_config(page_title="Hot Dog & Base Running Challenge", page_icon="🌭", layout="wide")

# Initialize session state
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'race_time' not in st.session_state:
    st.session_state.race_time = 0.0
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Title and description
st.markdown(
    "<h1 style='text-align: center;'><b>🌭 Hot Dog & Base Running Challenge 🏃‍♂️</b></h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h5 style='text-align: center;'><b>Joey Chestnut vs Bobby Witt Jr.</b></h5>",
    unsafe_allow_html=True
)

# Create a centered section
col1, col2, col3 = st.columns([1, 2, 1])

# Parameters in sidebar
st.sidebar.header("Adjust Parameters")
joey_hotdog_time = st.sidebar.slider("Joey's Hot Dog Time (s)", 2.0, 10.0, 5.0, 0.1)
joey_base_time = st.sidebar.slider("Joey's Base Running Time (s)", 20.0, 40.0, 30.0, 0.5)
bobby_hotdog_time = st.sidebar.slider("Bobby's Hot Dog Time (s)", 20.0, 40.0, 30.0, 0.5)
bobby_base_time = 14.3  # Fixed value

st.sidebar.info("**Bobby's Base Running:** Fixed at 14.3s (his fastest recorded home-to-home speed)")

# Control buttons
with col2:
    left_spacer, btn1_col, btn2_col, right_spacer = st.columns([1,2,2,1])
    with btn1_col:
        if st.button("▶️ Start" if not st.session_state.is_running else "⏸️ Pause", 
                     use_container_width=True):
            st.session_state.is_running = not st.session_state.is_running
            if st.session_state.is_running:
                st.session_state.start_time = time.time() - st.session_state.race_time
                st.session_state.winner = None
    with btn2_col:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.race_time = 0.0
            st.session_state.winner = None
            st.session_state.start_time = None
            
# Time display
with col2:
    # Create placeholder for dynamic time update
    time_placeholder = st.empty()
    time_placeholder.markdown(f"<h3 style='text-align: center;'><b>⏱️ Time: {st.session_state.race_time:.1f}s</center></b></h3>", unsafe_allow_html=True)

# Calculate progress
def calculate_progress(current_time, hotdog_time, base_time):
    hotdog_progress = min(current_time / hotdog_time, 1.0) if hotdog_time > 0 else 0
    base_progress = 0.0
    if current_time > hotdog_time:
        base_progress = min((current_time - hotdog_time) / base_time, 1.0) if base_time > 0 else 0
    return hotdog_progress, base_progress

# Calculate base position (adjusted for new field layout)
def get_base_position(progress):
    if progress <= 0.25:  # Home to 1st
        t = progress * 4
        x = 0.5 + t * 0.295
        y = 0.1 + t * 0.285
    elif progress <= 0.5:  # 1st to 2nd
        t = (progress - 0.25) * 4
        x = 0.795 - t * 0.295
        y = 0.385 + t * 0.265
    elif progress <= 0.75:  # 2nd to 3rd
        t = (progress - 0.5) * 4
        x = 0.5 - t * 0.295
        y = 0.65 - t * 0.265
    else:  # 3rd to home
        t = (progress - 0.75) * 4
        x = 0.205 + t * 0.295
        y = 0.385 - t * 0.285
    return x, y

# Create placeholders for dynamic content
winner_placeholder = st.empty()
progress_container = st.container()

# Function to draw everything
def draw_race_state():
    # Calculate current progress
    joey_hotdog_prog, joey_base_prog = calculate_progress(
        st.session_state.race_time, joey_hotdog_time, joey_base_time)
    bobby_hotdog_prog, bobby_base_prog = calculate_progress(
        st.session_state.race_time, bobby_hotdog_time, bobby_base_time)
    
    # Check for winner
    joey_finished = joey_hotdog_prog >= 1 and joey_base_prog >= 1
    bobby_finished = bobby_hotdog_prog >= 1 and bobby_base_prog >= 1
    
    if (joey_finished or bobby_finished) and not st.session_state.winner:
        st.session_state.is_running = False
        if joey_finished and bobby_finished:
            joey_total = joey_hotdog_time + joey_base_time
            bobby_total = bobby_hotdog_time + bobby_base_time
            st.session_state.winner = "Joey" if joey_total < bobby_total else "Bobby"
        elif joey_finished:
            st.session_state.winner = "Joey"
        else:
            st.session_state.winner = "Bobby"
    
    # Winner display
    with winner_placeholder.container():
        if st.session_state.winner:
            winner_name = "🌭 Joey Chestnut" if st.session_state.winner == "Joey" else "⚾ Bobby Witt Jr."
            if st.session_state.winner == "Joey":
                total_time = joey_hotdog_time + joey_base_time
                breakdown = f"Total time: {total_time:.1f}s ({joey_hotdog_time}s eating + {joey_base_time}s running)"
            else:
                total_time = bobby_hotdog_time + bobby_base_time
                breakdown = f"Total time: {total_time:.1f}s ({bobby_hotdog_time}s eating + {bobby_base_time}s running)"
            
            st.success(f"### 🏆 {winner_name} Wins!\n{breakdown}")
    
    # Progress visualization
    with progress_container:
        st.markdown("---")
        
        # HOT DOG EATING SECTION (ABOVE)
        st.markdown(f"<h3 style='text-align: center;'><b>🌭 Hot Dog Eating Speed</center></b></h3>", unsafe_allow_html=True)
        
        # Create two columns for hot dog progress bars
        hotdog_col1, hotdog_col2 = st.columns(2)
        
        with hotdog_col1:
            # Joey's progress
            st.markdown("**Joey Chestnut**")
            joey_percent = joey_hotdog_prog * 100
            st.progress(joey_hotdog_prog)
            if joey_hotdog_prog >= 1:
                st.caption(f"DONE! 🌭 ({joey_hotdog_time}s)")
            else:
                st.caption(f"{joey_percent:.0f}% - {min(st.session_state.race_time, joey_hotdog_time):.1f}s / {joey_hotdog_time}s")
        
        with hotdog_col2:
            # Bobby's progress
            st.markdown("**Bobby Witt Jr.**")
            bobby_percent = bobby_hotdog_prog * 100
            st.progress(bobby_hotdog_prog)
            if bobby_hotdog_prog >= 1:
                st.caption(f"DONE! 🌭 ({bobby_hotdog_time}s)")
            else:
                st.caption(f"{bobby_percent:.0f}% - {min(st.session_state.race_time, bobby_hotdog_time):.1f}s / {bobby_hotdog_time}s")
        
        # BASE RUNNING SECTION (BELOW)
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center;'><b>⚾ Base Running</center></b></h3>", unsafe_allow_html=True)
        
        # Center the baseball diamond
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            
            # Draw baseball field
            # Outfield (green background)
            ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#228B22'))
            
            # Draw the outfield arc
            
            # Infield dirt - create a more realistic infield shape
            # Main infield arc
            infield_arc = patches.Wedge((0.5, 0.1), 0.7, 45, 135, 
                                      facecolor='#8B7355', edgecolor=None)
            ax.add_patch(infield_arc)
            
            
            # Inner grass diamond
            grass_diamond = np.array([
                [0.5, 0.15],   # Behind home
                [0.75, 0.4],  # Toward first
                [0.5, 0.60],   # Behind second
                [0.25, 0.40],  # Toward third
                [0.5, 0.15]    # Back to home
            ])
            ax.add_patch(patches.Polygon(grass_diamond, facecolor='#228B22'))
            
            # Pitcher's mound circle
            pitcher_circle = plt.Circle((0.5, 0.37), 0.05, facecolor='#8B7355', edgecolor=None)
            ax.add_patch(pitcher_circle)
            
            # Pitcher's rubber
            ax.add_patch(plt.Rectangle((0.485, 0.365), 0.03, 0.01, 
                                     facecolor='white', edgecolor='black', linewidth=1))
            
            # Foul lines
            factor = 3  # Increase for longer lines

            # First base foul line
            x0, y0 = 0.5, 0.1
            x1, y1 = 0.95, 0.55
            dx, dy = x1 - x0, y1 - y0
            x2, y2 = x0 + dx * factor, y0 + dy * factor

            # Third base foul line
            x1b, y1b = 0.05, 0.55
            dx_b, dy_b = x1b - x0, y1b - y0
            x2b, y2b = x0 + dx_b * factor, y0 + dy_b * factor

            ax.plot([x0, x2], [y0, y2], 'white', linewidth=2, zorder=2)
            ax.plot([x0, x2b], [y0, y2b], 'white', linewidth=2, zorder=2)

            
            # Bases
            base_size = 0.03
            # Home plate (pentagon shape)
            home_x, home_y = 0.5, 0.1
            shift = 0.77 # try 0.05-0.1 for gentle moves, increase if needed

            home_plate_pts = np.array([
                [home_x - 0.02, 1 - home_y - shift],
                [home_x - 0.02, 1 - (home_y + 0.02) - shift],
                [home_x,        1 - (home_y + 0.03) - shift],
                [home_x + 0.02, 1 - (home_y + 0.02) - shift],
                [home_x + 0.02, 1 - home_y - shift],
                [home_x - 0.02, 1 - home_y - shift]
            ])
            # Bases (higher zorder so they appear on top)
            ax.add_patch(patches.Polygon(home_plate_pts, facecolor='white', 
                                        edgecolor='black', linewidth=2, zorder=10))
            ax.add_patch(plt.Rectangle((0.79, 0.39), base_size, base_size, 
                                    facecolor='white', edgecolor='black', angle=45, linewidth=2, zorder=10))
            ax.add_patch(patches.RegularPolygon((0.5, 0.66), 4, radius=0.02,
                                            orientation=np.pi/4,
                                            facecolor='white', edgecolor='black', linewidth=2, zorder=10))
            ax.add_patch(plt.Rectangle((0.19, 0.41), base_size, base_size,
                                    facecolor='white', edgecolor='black', angle=-45, linewidth=2, zorder=10))
            
            # Draw runners if they're on the bases
            if st.session_state.race_time > joey_hotdog_time and joey_base_prog > 0:
                joey_x, joey_y = get_base_position(joey_base_prog)
                ax.add_patch(plt.Circle((joey_x, joey_y), 0.025, facecolor='#DC2626', 
                                       edgecolor='white', linewidth=2, zorder=20))
            
            if st.session_state.race_time > bobby_hotdog_time and bobby_base_prog > 0:
                bobby_x, bobby_y = get_base_position(bobby_base_prog)
                ax.add_patch(plt.Circle((bobby_x, bobby_y), 0.025, facecolor='#2563EB', 
                                       edgecolor='white', linewidth=2, zorder=20))
            
            ax.axis('off')
            st.pyplot(fig, clear_figure=True)
            
            # Centered legend below the image
            st.markdown("<center>🔴 <b>Joey</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🔵 <b>Bobby</b></center>", unsafe_allow_html=True)
            
            # Base running progress text (centered)
            joey_base_percent = joey_base_prog * 100 if st.session_state.race_time > joey_hotdog_time else 0
            bobby_base_percent = bobby_base_prog * 100 if st.session_state.race_time > bobby_hotdog_time else 0
            st.markdown(f"<center>Joey: {joey_base_percent:.0f}% around bases | Bobby: {bobby_base_percent:.0f}% around bases</center>", unsafe_allow_html=True)
        
        # Analysis section
        if st.session_state.winner:
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>Race Analysis</h3>", unsafe_allow_html=True)
            
            joey_total = joey_hotdog_time + joey_base_time
            bobby_total = bobby_hotdog_time + bobby_base_time
            
            # Stack the analysis sections vertically
            st.markdown("#### 🌭 Joey's Two-Phase Attack")
            st.write(f"Joey dominates the hot dog phase ({joey_hotdog_time}s) but struggles on the bases ({joey_base_time}s).")
            st.write(f"Total time: {joey_total:.1f}s")
            
            st.markdown("#### ⚾ Bobby's Balanced Approach")
            st.write(f"Bobby takes his time with the hot dog ({bobby_hotdog_time}s) but flies around the bases (14.3s - his fastest recorded time).")
            st.write(f"Total time: {bobby_total:.1f}s")
            
            if joey_total < bobby_total:
                difference = bobby_total - joey_total
                st.info(f"**The Real Battle:** Joey wins by {difference:.1f} seconds! His hot dog mastery creates an insurmountable lead despite Bobby's base running advantage.")
            else:
                difference = joey_total - bobby_total
                st.info(f"**The Real Battle:** Bobby wins by {difference:.1f} seconds! Even with Joey's hot dog dominance, Bobby's elite speed and more reasonable eating pace wins out.")

# Draw initial state
draw_race_state()

# Auto-update loop
if st.session_state.is_running:
    # Update race time
    st.session_state.race_time = time.time() - st.session_state.start_time
    time_placeholder.markdown(f"<h3 style='text-align: center;'><b>⏱️ Time: {st.session_state.race_time:.1f}s</center></b></h3>", unsafe_allow_html=True)
    
    # Short delay then rerun
    time.sleep(0.1)
    st.rerun()

# Add a note about real-time updates
if not st.session_state.is_running and st.session_state.race_time == 0:
    st.markdown("---")
    st.info("👆 Click 'Start' to begin the race! Adjust the parameters in the sidebar to see how different speeds affect the outcome.")