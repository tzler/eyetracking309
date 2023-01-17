from psychopy import core, visual, event, monitors
from datetime import datetime
import os, time, sys, pandas, numpy as np
import pylink, eyelink_functions

def generate_differentmatch(params, trialinfo):
    
    def flip_value(x, i): 
        """flip the value of the string (0->1| 1->0) at a given index"""
        return str(abs(int(x[i])-1))
    def random_value():
        """just generates a random 1 or 0 formatted as a string"""
        return str(np.random.randint(2))
    
    # extract name of object
    name = trialinfo['sample_identity'] 
    
    if params['distance_protocol'] == 'uniform':
        # change everything with equal probability
        i_distance = np.random.permutation([0, 1, 2])[0] 
    elif params['distance_protocol'] == 'same_surface': 
        # only select pairs that have the same surface
        i_distance = np.random.permutation([0, 1])[0] 
    elif params['distance_protocol'] == 'small_component_shift': 
        # pair objects that only vary in small component
        i_distance = 0
    
    if i_distance == 0: 
        # only changes the small-component configuration
        match_identity = name[0:2] + flip_value(name, 2) 
    if i_distance == 1:                                  
        # changes the large component configuration + randomizes small component
        match_identity = name[0] + flip_value(name,1) + random_value() 
    if i_distance == 2:                                                          
        #changes large component + randomizes large/small components
        match_identity = flip_value(name,0) + random_value() + random_value() 
    
    return match_identity 

def get_identity(x): 
    return x[4:7]

def get_viewpoint(x): 
    return x[8:14] 
 
def generate_match_images(params, trial_info): 
   
    # get all images in this experiment 
    images = np.random.permutation(os.listdir(params['image_directory']))
    
        
    if params['stimulus_set'] == 'barense': 
        
        #print( 'setting up barense sequential mts trial')  

        # get all images in this experiment
        images = np.random.permutation(os.listdir(params['image_directory']))

        # find other images 
        trial_oddity = trial_info['sample_image'] 
        trial_screen = trial_oddity[:22] 
        all_typicals = [i for i in os.listdir(params['image_directory']) if (trial_screen in i) * ('oddity' not in i) ]
        trial_images = list( np.random.permutation(all_typicals)[:2]   ) 

        #oddity_location = np.random.randint(3)
        #rrial_images.insert(oddity_location, trial_oddity)
        #same_different_options = {'same': match_image, 'different': foil_image}
        #print('EXIT') 
        exit()
    else: 
        # determine what identity of trial image is 
        trial_info['sample_identity'] = sample_identity = get_identity( trial_info['sample_image'] ) 
        # determine what the viewpoint of the trial image is 
        trial_info['sample_viewpoint'] = sample_view = get_viewpoint( trial_info['sample_image'] ) 

        #print( '-----', sample_identity, sample_view, )     
        # find other rotations of sample image
        sample_rotations = [i for i in images if (sample_identity in i) * (sample_view not in i) ]
        # select a different rotation of the sample image 
        match_image = np.random.permutation(sample_rotations)[0]
        
        # generate a match identity that's different from the sample image 
        foil = generate_differentmatch(params, trial_info) 
        # identify all images with this match identity that have a different viewpoint than the sample image
        foil_images = [i for i in images if (foil in i) * (sample_view not in i) * (get_viewpoint(match_image) not in i) ]
        # select a single image of this different identity 
        foil_image = np.random.permutation(foil_images)[0] 
        # create single dictionary with both possibilities
        same_different_options = {'same': match_image, 'different': foil_image}
    
    return same_different_options, trial_info

def setup_match_screen(window, params, trial_info): 
    """generates a pair of possible match-screen images and selects these based on the experimental protocol"""
    
    #matches = {'same': trial_info#trial_info = generate_match_images(params, trial_info) 
    
    # define match image   
    if params['match_screen_type'] == 'single': 
        
        ######## makes this a sequential same-different task
        
        # randomly determine whether this will be a same or different trial (and save this value)
        trial_answer = ['different', 'same'] [ 1 * (np.random.random() > params['proportion_same'])]
        # select the image we've generated for this (either same or different) trial         
        match_screen_image = matches[ trial_answer ]
        # generate the path to this image 
        match_image_path = os.path.join(params['image_directory'], match_screen_image) 
        # define match image
        match_stimulus = visual.ImageStim(window, image=match_image_path)
        # project sample image on the back-screen 
        match_stimulus.draw()
        
        # save information into trialdata for later analysis
        trial_info['keyboard_map'] = params['keyboard_map'] #{'0':'different', '1':'same'}
        trial_info['answer'] = trial_answer 
        trial_info['match_image'] = match_screen_image
        trial_info['match_identity'] = get_identity(match_screen_image) 
        trial_info['match_viewpoint'] = get_viewpoint(match_screen_image) 
    
    elif params['match_screen_type'] == 'double': 
        
        ######### makes this a sequential match-to-sample task
        
        # determine whether the correct answer is going to be on the left or right 
        trial_answer = ['left', 'right'] [ 1 * (np.random.random()>.5)] 
        # decide how much to shift each image by (here, i think .5 = half the distance from 0,0 to the edge
        if params['units_of_screen'] == 'deg': 
            shift = [-params['shift_xy'], params['shift_xy'] ] 
        else: 
            shift = [ -(params['screen_width']/5) , params['screen_width']/5]  
        
	# determine the path to the same and different images 
        match_image_path = trial_info['stimuli']['paths']['typical1']
        diff_image_path =  trial_info['stimuli']['paths']['oddity']
 
        # position and same and different images on either the left or right of the screen 
        match_stimulus = visual.ImageStim(window, image=match_image_path, pos=(shift[trial_answer=='right'], 0))
        diff_stimulus = visual.ImageStim(window, image=diff_image_path, pos=(shift[trial_answer!='right'], 0))
        
        # project sample image on the back-screen 
        match_stimulus.draw()
        diff_stimulus.draw()
        #print( 'match_stimulus', match_stimulus, 'diff_stimulus', diff_stimulus ) 
     
        # save infomation into trial data for later analysis
        trial_info['keyboard_map'] = params['keyboard_map'] # {'1': 'left', '0': 'right'} 
        trial_info['matchscreen_image_same'] = trial_info['stimuli']['typicals'][1] #matches['same'] 
        trial_info['answer'] = trial_answer 
        trial_info['matchscreen_image_different'] = trial_info['stimuli']['oddity'] #matches['different'] 
        trial_info['matchscreen_matchside'] = trial_answer 
        trial_info['samplescreen_image'] = trial_info['stimuli']['typicals'][0]
        # save match scareen image metadata     
        trial_info['matchscreen_image_match_position'] = match_stimulus.pos
        trial_info['matchscreen_image_match_size'] = match_stimulus.size
        trial_info['matchscreen_image_match_units'] = match_stimulus.units
        
        # save match scareen image metadata     
        trial_info['matchscreen_image_distractor_position'] = diff_stimulus.pos
        trial_info['matchscreen_image_distractor_size'] = diff_stimulus.size
        trial_info['matchscreen_image_distractor_units'] = diff_stimulus.units
	
	# save image-related info
    # REMEMBER: we haven't visualize match screen at the point 
    # clear the keyboard buffer (for memory + data collection purposes) 
    event.clearEvents()        
 
    return window, trial_info

def generate_mask(window, image_path, seconds_to_display): 
    """generates a mask using the sample image"""
    
    # dont understand the details about this function yet 
    #noise1 = noise = visual.NoiseStim(
    #            win=window, name='noise',units='pix',
    #            noiseImage=image_path, 
    #            mask='circle',
    #            ori=1.0, pos=(0, 0), size=(512, 512), sf=None, phase=.5,
    #            color=[.5, .5, .5], colorSpace='rgb', opacity=1, blendmode='add', contrast=.5,
    #            #texRes=1024,
    #            #filter='None', 
    #            #imageComponent='Phase', 
    #            noiseType='image', #'white', 
    #            noiseElementSize=4, 
    #            noiseBaseSf=32.0/512,
    #            )

    # https://discourse.psychopy.org/t/builder-noisestim-to-imagestim/16146
    noise = visual.NoiseStim(
        win=window, name='noise',units='pix',
        noiseImage=image_path, mask='circle',
        ori=0, pos=[0,0], size=(500, 500), sf=None,
        phase=0.0,
        color=[1,1,1], colorSpace='rgb', opacity=.3, blendmode='avg', contrast=1,
        texRes=128, filter=None,
        noiseType='Image', noiseElementSize=0.0625,
        noiseBaseSf=8.0, noiseBW=1,
        noiseBWO=30, noiseOri=0.0,
        noiseFractalPower=0.0,noiseFilterLower=1.0,
        noiseFilterUpper=8.0, noiseFilterOrder=0.0,
        noiseClip=3.0, imageComponent='Phase', interpolate=False, depth=-2.0)

    #build the noise 
    noise.buildNoise()

    # draw mask on the back screen 
    noise.draw() 
    # show mask 
    window.flip()
    # determine time of mask
    clock = core.Clock()
    # wait for alotted time 
    while clock.getTime() < seconds_to_display: 
        pass
    # remove mask — by displaying nothing 
    window.flip()

def pre_trial_setup(window, genv, params): 
    """ 
    1. ask for keypress to initiate trial
    2. recalibrate using a fixation 
    3. return eyetracker object prepped for trial 
    """
    
    # define text to show at beginning of/to initiate each trial 
    initiate_trial_screen = visual.TextStim(window, 'press spacebar to begin the next trial', color=(0, 0, 0)) 
    # draw on back screen 
    initiate_trial_screen.draw()
    # display back screen 
    window.flip()
    # wait for keyboard response to initiate trial 
    if event.waitKeys()[0] == 'space': 
        pass
    elif event.waitKeys()[0] in ['q', 'escape']: 
        exit() 
    
	# gaze recalibration from fixation
    el_tracker = eyetracker_setup_for_trial(window, genv, params) 

    return el_tracker

def sample_screen_protocol(window, genv, el_tracker, params, trial_info): 
    """ present stimulus, collect gaze+keyboard behavior, mask image"""  
 
    # set the path to trial image  
    sample_image_path = os.path.join(params['image_directory'], trial_info['stimuli']['typicals'][0])
    
    # define sample image
    sample_stimulus = visual.ImageStim(window, image=sample_image_path)
    
    # project sample image on the back-screen 
    sample_stimulus.draw()
    # display stimulus on front screen
    window.flip() 
    
    # save sample image metadata     
    trial_info['sample_image_position'] = sample_stimulus.pos
    trial_info['sample_image_size'] = sample_stimulus.size
    trial_info['sample_imae_units'] = sample_stimulus.units
 
    # collect gaze and keyboard behavior 
    trial_info = collect_behavior(window, genv, el_tracker, params, trial_info, 'sample') 
    
    # masking protocol
    if params['use_mask']: 
        print("MASKING?") 
        generate_mask(window, sample_image_path, params['masktime']) 
    
    return trial_info 

def feedback_protocol(window, params, response):
    """doesnt end trial, but replaces image with feedback (correct/incorrect)"""
    if params['feedback']: 
        # determine color of trial feedback 
        feedback_color = [params['wrong_rgb'], params['right_rgb']][  response ] 
        # determine trial text 
        feedback_text =  ['incorrect! D:', 'correct! :D'][ response ]
        # create feedback text/color
        trial_feedback = visual.TextStim(window, feedback_text, color=feedback_color)
        # draw on back window
        trial_feedback.draw() 
        # show back window
        window.flip() 
        # wait for given amount of time, depending on correct/incorrect
	
        core.wait( [params['wrongtime'], params['righttime']][response])

def collect_behavior(window, genv, el_tracker, params, trial_info, screen): 

    gaze_pos = (None, None) 
    gaze_x = [] 
    gaze_y = [] 
    time_i = [] 

    # determine how much time to allow for this trial
    if params['sample_timing'] == 'self_paced' or screen=='match':
        # for self paced sample screen + match screen trials allow ten seconds 
        time_alotted = params['self_paced_timeout'] 
    elif params['sample_timing']=='variable' and screen=='sample': 
        # determine random presentation time between given intervals 
        time_alotted = np.random.uniform(params['sampletime'][0], params['sampletime'][1])
    elif params['sample_timing'] == 'fixed' and screen=='sample': 
        # extract given timing for all trials 
        time_alotted = params['sampletime'][0] 
 
    # make the back-screen the front-screen  
    ############## if screen=='match': window.flip() #################### check if this is right  
    # time image presentation 
    stimulus_time = core.Clock()
    # initialize keyboard result variable  
    trial_info['%s_response'%screen] = None

    # start gaze recording 
    el_tracker = start_gaze_recording(el_tracker) 
    # determine which eye the tracker is using  
    eye_used = el_tracker.eyeAvailable() 

    while trial_info['%s_response'%screen] == None: 
        
        # first, let's stream data from the eyetracker
        current_sample = el_tracker.getNewestSample() 

        # figure out how to deal with these... 
        if current_sample is None:  # no sample data
            gaze_pos = (None, None)
        else:
            if eye_used == 1 and current_sample.isRightSample():
                gaze_pos = current_sample.getRightEye().getGaze()
            elif eye_used == 0 and current_sample.isLeftSample():
                gaze_pos = current_sample.getLeftEye().getGaze()
			
            # convert gaze information into screen's coordinate frame
            gaze_x.append( gaze_pos[0] - params['screen_width'] / 2.0 ) 
            gaze_y.append( params['screen_height']/ 2.0 - gaze_pos[1] )
            time_i.append( stimulus_time.getTime() )
            
            #if params['verbose']: print( gaze_x[-1] ) 
  			
        # now, let's deal with the keyboard responses 
        keyboard_response = event.getKeys() 
        
        # check for responses only on the match screens unless it's self paced 
        if screen=='match' or params['sample_timing']=='self_paced':  

            # whenever there's a keyboard press 
            if len(keyboard_response): 

                # manage participant decisions for match screens
                if keyboard_response[0] in params['keyboard_map'] and screen=='match':
                
                    # convert keyboard response into experimental decision 
                    trial_info['participant_decision'] = params['keyboard_map'][keyboard_response[0]] 
                    # determine whether the participant was correct/incorrect
                    trial_info['correct'] = 1 * (trial_info['answer'] == trial_info['participant_decision'] )
                    # recognize response and exit loop 
                    trial_info['%s_response'%screen] = True
                    # stop recording gaze behaviors 
                    stop_gaze_recording(el_tracker)                     
                    # give feedback when specified  
                    if screen=='match': feedback_protocol(window, params, trial_info['correct']) 
           		
                # manage participant responses for sample screens, when self paced 
                if keyboard_response[0] == params['proceed_key'] and screen=='sample': 

                    # register response to move on               
                    trial_info['%s_response'%screen] = True
                    # stop recording gaze behaviors 
                    stop_gaze_recording(el_tracker)                     

                # allow participants to exit experiments at the end of each trial 
                elif keyboard_response[0] in ['q', 'escape']:
                    # begin termination protocols 
                    eyelink_functions.terminate_task(experiment_window, genv, params) 
                    # close experiment window 
                    experiment_window.close()
                    # close psychopy 
                    core.quit()
   
        # break out of while loop if we're over time 
        if stimulus_time.getTime() > time_alotted:
            if screen=='match' and trial_info['%s_response'%screen] == None: 
                # mark lack of response  
                trial_info['participant_decision'] = None
                # mark incorrect 
                trial_info['correct'] = 0
                # give feedback
                feedback_protocol(window, params, trial_info['correct']) 

            break   
    
    # stop eye tracker 
    stop_gaze_recording(el_tracker) 
    # clear out the memory buffer 
    event.clearEvents()

    # measure actual time required for all observation types 
    trial_info['%sscreen_time'%screen] = stimulus_time.getTime()
    trial_info['%sscreen_gazex'%screen] = gaze_x 
    trial_info['%sscreen_gazey'%screen] = gaze_y 
    trial_info['%sscreen_timei'%screen] = time_i

    return trial_info

def match_screen_protocol(window, genv, el_tracker, params, trial_info): 
    
    # setup--don't show yet--match screen in preparation for data collection  
    window, trial_info = setup_match_screen(window, params, trial_info) 
 
    # show the match screen which is prepped 
    window.flip()

    # collect gaze and keyboard behavioral data
    trial_info = collect_behavior(window, genv, el_tracker, params, trial_info, 'match')
   
    return trial_info 

def concurrent_protocol(window, genv, el_tracker, params, trial_info): 
   
    #print( 'oddity_screen_protoco: trial_Info', trial_info )  

    # get all images in this experiment
    images = np.random.permutation(os.listdir(params['image_directory']))
    # determine what identity of trial image is
    #trial_info['sample_identity'] = get_identity( trial_info['sample_image'] )
    # determine what the viewpoint of the trial image is
    #trial_info['sample_viewpoint'] = sample_view = get_viewpoint( trial_info['sample_image'] )

    # find other images 
    trial_oddity = trial_info['sample_image'] 
    trial_screen = trial_oddity[:22] 
    all_typicals = [i for i in os.listdir(params['image_directory']) if (trial_screen in i) * ('oddity' not in i) ]
    trial_images = list( np.random.permutation(all_typicals)[:2]   ) 

    oddity_location = np.random.randint(3)
    trial_images.insert(oddity_location, trial_oddity)
    
    #sample_rotations = [i for i in images if (sample_identity in i) * (sample_view not in i) ]
    # select a different rotation of the sample image
    #match_image = np.random.permutation(sample_rotations)[0]

    # generate a match identity that's different from the sample image
    #foil = generate_differentmatch(params, trial_info)
    # identify all images with this match identity that have a different viewpoint than the sample image
    #foil_images = [i for i in images if (foil in i) * (sample_view not in i) * (get_viewpoint(match_image) not in i) ]
    # select a single image of this different identity
    #foil_image = np.random.permutation(foil_images)[0]
    # create single dictionary with both possibilities
    #same_different_options = {'same': match_image, 'different': foil_image}

    #return same_different_options, trial_info


    # determine whether the correct answer is going to be on the left or right
    #trial_answer = ['left', 'right'] [ 1 * (np.random.random()>.5)]
    # decide how much to shift each image by (here, i think .5 = half the distance from 0,0 to the edge
    shiftx = params['screen_width']/5
    shifty = params['screen_height']/5

    # determine the path to the same and different images
    #match_image_path = os.path.join(params['image_directory'], matches['same'])
    #diff_image_path =  os.path.join(params['image_directory'], matches['different'])

    image0 = os.path.join(params['image_directory'], trial_images[0])
    image1 = os.path.join(params['image_directory'], trial_images[1])
    image2 = os.path.join(params['image_directory'], trial_images[2])

    stimulus0 = visual.ImageStim(window, image=image0, pos=(-shiftx, shifty))
    stimulus1 = visual.ImageStim(window, image=image1, pos=(shiftx, shifty))
    stimulus2 = visual.ImageStim(window, image=image2, pos=(0, -shifty))

    verbose_name = visual.TextStim(window, trial_oddity, color=(1,1,1))
    verbose_name.draw() 
    
    # position and same and different images on either the left or right of the screen
    #match_stimulus = visual.ImageStim(window, image=match_image_path, pos=(shift[trial_answer=='right'], 0))
    #diff_stimulus = visual.ImageStim(window, image=diff_image_path, pos=(shift[trial_answer!='right'], 0))

    # project sample image on the back-screen
    #match_stimulus.draw()
    #diff_stimulus.draw()


    stimulus0.draw() 
    stimulus1.draw()
    stimulus2.draw()     

    # save infomation into trial data for later analysis
    trial_info['keyboard_map'] = params['keyboard_map'] # {'1': 'left', '0': 'right'}
#    trial_info['matchscreen_same'] = matches['same']
    trial_info['answer'] = oddity_location # trial_answer
#    trial_info['matchscreen_same_identity'] = get_identity(matches['same'] )
#    trial_info['matchscreen_same_viewpoint'] = get_viewpoint(matches['same'])
#    trial_info['matchscreen_different'] = matches['different']
#    trial_info['matchscreen_different_identity'] = get_identity(matches['different'] )
#    trial_info['matchscreen_different_viewpoint'] = get_viewpoint(matches['different'])

 
    # randomly determine whether this will be a same or different trial (and save this value)
#    trial_answer = 'same' # ['different', 'same'] [ 1 * (np.random.random() > params['proportion_same'])]
    # select the image we've generated for this (either same or different) trial         
#    match_screen_image = 'same' # matches[ trial_answer ]
    # generate the path to this image 
#    oddity_screen_path = os.path.join(params['image_directory'], trial_info['sample_image']) 
    # define match image
#    oddity_screen = visual.ImageStim(window, image=oddity_screen_path)
    # project sample image on the back-screen 
#    oddity_screen.draw()
    # save information into trialdata for later analysis
#    trial_info['keyboard_map'] = params['keyboard_map'] #{'0':'different', '1':'same'}
#    trial_info['answer'] = trial_answer 
#    trial_info['match_image'] = match_screen_image
    #trial_info['match_identity'] = get_identity(match_screen_image) 
    #trial_info['match_viewpoint'] = get_viewpoint(match_screen_image) 
 
    # show the match screen which is prepped 
    window.flip()
   
    # collect gaze and keyboard behavioral data
    trial_info = collect_behavior(window, genv, el_tracker, params, trial_info, 'match')
   
    return trial_info 

def get_trial_images(params, trial_oddity): 
    
    if params['stimulus_set'] == 'barense':

        # get the screen for all images in this trial   
        i_screen = trial_oddity[:22] 
        # get all other images--i.e. typicals--in this screen
        all_typicals = [i for i in os.listdir(params['image_directory']) if (i_screen in i) * ('oddity' not in i) ]
        # define the images we're going to use on this trial
        trial_typicals = list( np.random.permutation(all_typicals)[:2]  ) 
        
        trial_paths = {'oddity':  os.path.join(params['image_directory'], trial_oddity), 
                       'typical0':  os.path.join(params['image_directory'], trial_typicals[0]), 
                       'typical1':  os.path.join(params['image_directory'], trial_typicals[1])}

        trial_images = {'paths': trial_paths, 'oddity': trial_oddity, 'typicals': trial_typicals}
    
    return trial_images

def run_single_trial(window, genv, sample_image, params): 
   
    trial_info = {'stimuli': get_trial_images(params, sample_image) }

    if params['experiment_type'] == 'sequential':  
        
        # prep eyetracker for trial  
        el_tracker = pre_trial_setup(window, genv, params)

        # show sample screen and collect gaze data 
        trial_info = sample_screen_protocol(window, genv, el_tracker, params, trial_info)
        
        # collect responses on match screen 
        trial_info = match_screen_protocol(window, genv, el_tracker, params, trial_info)   
   	 
    elif params['experiment_type'] == 'concurrent': 
        
        # prep eyetracker for trial  
        el_tracker = pre_trial_setup(window, genv, params)

        # show sample screen and collect gaze data 
        trial_info = concurrent_protocol(window, genv, el_tracker, params, trial_info)

    # migrate all the parameter information over to the trial data
    for i_param in params: trial_info[i_param] = params[i_param]
    
    #if params['verbose']: print('\n\nDATA\n', trial_info) 
    
    return trial_info 

def eyetracker_setup_for_trial(win, genv, params): 

    scn_width = params['screen_width']
    scn_height = params['screen_height']

    # get a reference to the currently active EyeLink connection
    el_tracker = pylink.getEYELINK()

    # put the tracker in the offline mode first
    el_tracker.setOfflineMode()
    
    ######el_tracker.sendMessage('TRIALID %d' % trial_index)

    # terminate the task if no longer connected to the tracker or
    if (not el_tracker.isConnected()) or el_tracker.breakPressed():
        eyelink_functions.terminate_task(win, genv, params)
        return pylink.ABORT_EXPT
    # drift-check and re-do camera setup if ESCAPE is pressed
    try:
        error = el_tracker.doDriftCorrect(int(scn_width/2.0), int(scn_height/2.0), 1, 1)
        # break following a success drift-check
        if error is not pylink.ESC_KEY:
            pass
    except:
        print('failed to drift correct') 

    # put tracker in idle/offline mode before recording
    el_tracker.setOfflineMode()

    return el_tracker


def start_gaze_recording(el_tracker): 

    # start recording
    try:
        el_tracker.startRecording(1, 1, 1, 1)
    except RuntimeError as error:
        print("ERROR:", error)
        eyelink_functions.abort_trial(win, genv)
        return pylink.TRIAL_ERROR

    # Allocate some time for the tracker to cache some samples
    pylink.pumpDelay(100)
	
    return el_tracker

def stop_gaze_recording(el_tracker): 

    # stop recording; add 100 msec to catch final events before stopping
    pylink.pumpDelay(100)
    el_tracker.stopRecording()

    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)


def generate_subject_id(path_to_data, subject_id=None): 
    """generate id used to save data — build it out after talking with Akshay"""
    
    # get a list of previous subjects 
    # past_subjects = np.unique( [i[7:10] for i in os.listdir(path_to_data) if 'subject' in i]  )
    
    past_subjects = [i for i in os.listdir(path_to_data) if 'subject' in i]
    
    # check for command line arguments
    #if len(sys.argv) > 2: 
    #    
    #    # if arg can be converted into a number
    #    try: 
    #        # nice spacing 
    #        possible_id = '%03d'%(int(sys.argv[2]))
    #        # check if it's unique
    #        if possible_id not in past_subjects: 
    #            # define new subject_id
    #            subject_id = possible_id
    #    # otherwise, just use it as a string 
    #    except: 
    #        subject_id = sys.argv[2] 
    
    # if the subject_id is still not defined
    if subject_id == None: 
        # generate the next subject id in the folder
        subject_id = '%03d'%(len(past_subjects))
   
    return 'subject%s_%s'%(subject_id, datetime.today().strftime("%d_%m_%Y"))

def image_order_protocol(params): 
    """determine the order that images will be presented in"""
    
    if params['stimulus_set'] == 'barense': 
        files = [i for i in os.listdir(params['image_directory']) if 'oddity' in i]
        images = np.random.permutation(files)
        #print( 'barense images', images ) 

    
    else: # params['sample_image_protocol'] == 'shuffle': 
        # for the moment, shuffle experimmental images
        files = [i for i in os.listdir(params['image_directory']) if 'view' in i]
        images = np.random.permutation(files)
    
    
    return images

def setup_eyelink_for_experiment(params): 

    # Switch to the script folder
    script_path = os.path.dirname(sys.argv[0])
    if len(script_path) != 0:
        os.chdir(script_path)

    #params = eyelink_functions.setup_edf_file(params)

    el_tracker = eyelink_functions.connect_to_eyelink(params)
	
    #params = eyelink_functions.open_edf_file(params, el_tracker) 
	
    eyelink_functions.configure_tracker(el_tracker, params) 
    #print( 'params', params) 
    win, genv, params = eyelink_functions.setup_graphics_environment_for_calibration(el_tracker, params)

    #eyelink_functions.eyeTrkCalib(el_tracker, (1900, 1200), 32) 
    eyelink_functions.setup_calibration_target(genv, params)

    ###################### Step 5: Set up the camera and calibrate the tracker

    # Show the task instructions
    task_msg = 'In the task, you may press the SPACEBAR to end a trial\n' + \
        '\nPress Ctrl-C to if you need to quit the task early\n'
    if params['dummy_mode']:
        task_msg = task_msg + '\nNow, press ENTER to start the task'
    else:
        task_msg = task_msg + '\nNow, press ENTER twice to calibrate tracker'
    eyelink_functions.show_msg(params, win, genv, task_msg)

    # skip this step if running the script in Dummy Mode
    if not params['dummy_mode']:
        try:
            el_tracker.doTrackerSetup()
        except RuntimeError as err:
            print('ERROR:', err)
            el_tracker.exitCalibration()
    
    print('eyetracker sucessfully setup!') 

    return win, genv, params, el_tracker

def setup_camera_and_calibrate(win, el_tracker, params): 

    # Step 5: Set up the camera and calibrate the tracker

    # Show the task instructions
    task_msg = 'In the task, you may press the SPACEBAR to end a trial\n' + \
        '\nPress Ctrl-C to if you need to quit the task early\n'
    if params['dummy_mode']:
        task_msg = task_msg + '\nNow, press ENTER to start the task'
    else:
        task_msg = task_msg + '\nNow, press ENTER twice to calibrate tracker'
    eyelink_functions.show_msg(params, win, genv, task_msg)

    # skip this step if running the script in Dummy Mode
    if not params['dummy_mode']:
        try:
            el_tracker.doTrackerSetup()
        except RuntimeError as err:
            print('ERROR:', err)
            el_tracker.exitCalibration()


if __name__ == '__main__': 
    
    params = {
        # concurrent | sequential 
        'experiment_type': 'sequential', 
        'stimulus_set': 'barense', 
        # how to generate sample images
        'sample_image_protocol': 'shuffle', 
        # how to generate the distractor
        'distance_protocol': 'uniform',
        # keys to escape the experiment
        'escape_keys': ['q', 'escape'],
        # show sample for ... 'self_paced' 'variable' 'fixed'
        'keyboard_map': {'1': 'left', '0': 'right'},
        # 
        'proceed_key': 'space',  
        'sample_timing': 'self_paced',  
        # set timeout for self paced + match screen (in seconds) 
        'self_paced_timeout': 10, 
        # time on sample screen if not self paced--a list w/ 1|2 numbers 
        'sampletime': [.2, 1] , 
        # entering into fullscreen 
        'full_screen': True, 
        # ratio of same/different 
        'proportion_same': .5, 
        # experiment type: 2|1 ('double'|'single') images on match screen
        'match_screen_type': 'double',
        # absolute path to images, which should be in this directory
        #'image_directory': os.path.join(os.getcwd(),'../stimuli/barense_2007/'),  
        # backwards mask over image 
        'use_mask': False, 
        # time to mask in seconds 
        'masktime': .01,
        # feedback after each trial
        'feedback': True, 
        # color of wrong trials feedback
        'wrong_rgb': (1,0,0), 
        # color of right trials feedback
        'right_rgb': (0,1,0), 
        # time to wait when wrong
        'wrongtime': 1., 
        # time to wait when right
        'righttime':.4,
        # print out data from the terminal 
	'verbose': False,
        # eyelink integration params
        'use_retina': False, 
        # decide whether we're actually running eyetracker 
        'dummy_mode': False,
        'fixation_image_location':  os.path.join(os.getcwd(),'../stimuli/fixTarget_white.bmp'),  
        'units_of_screen': 'pix', # either 'deg' for degrees of visual angle or 'pix' for pixels
        'distance_to_monitor': 50, # measured distance from head position to monitor (in cm) 
        'monitor_width_in_cm': 52.0 , #55.1, #60.96,
        'monitor_size_in_pixels': (1920, 1200), #1080), # touple    
        'shift_xy': 10, # amount to shift in degrees of visual angle
 
        'experiment_length': 50,
        'block_length': 5, 
        'results_folder': '/Users/gru/psychopy/309_eyetracking_experiment/results/',  

}
   
    if params['stimulus_set'] == 'barense': 
        params['image_directory'] = os.path.join(os.getcwd(),'../stimuli/barense_2007/')

    if params['experiment_type'] == 'concurrent': 
        params['keyboard_map'] = {'left': 0, 'right': 1, 'down': 2}
    elif params['experiment_type'] == 'sequential':
        params['keyboard_map'] = {'1': 'left', '0': 'right'}
        
    i_trial = 0 
    run_experiment = True
    n_practice_trials = 5
    between_block_message = "Take a moment to rest and re-adjust your posture, then we'll re-calibrate and start again"
    
    if sum(['load_subject' in i for i in sys.argv]) : 
        name_from_input = [i[i.find('=')+1:] for i in sys.argv if 'subject' in i][0] 
        subject_id = [i for i in os.listdir(params['results_folder']) if name_from_input in i][0]  
        subject_file = os.path.join(params['results_folder'], subject_id) 
        experiment_data = pandas.read_csv(subject_file) 
        phase = 'experiment' 
        block_starttime = time.time() 
        experiment_starttime = time.time() 
        print('\n\n\n-----SUBJECT DATA FROM FILE:', subject_file)
    
    else: 
        
        # generate a subject id we can use to save data from this experiment
        subject_id = generate_subject_id(params['results_folder']) 
        subject_id + '.csv'
        # create dataframe for all trials in experiment 
        experiment_data = pandas.DataFrame({}) 
        phase = 'practice' 
        print('\n\n\n-----CREATING NEW SUBJECT', subject_id) 
    
    if sum(['experiment_length' in i for i in sys.argv]) : 
        experiment_length = [int(i[i.find('=')+1:]) for i in sys.argv if 'experiment_length' in i][0]
    else: 
        experiment_length = params['experiment_length'] 

    if sum(['block_length' in i for i in sys.argv]) : 
        block_length = [int(i[i.find('=')+1:]) for i in sys.argv if 'block_length' in i][0]
    else: 
        block_length = params['block_length'] 

    print('\n\n-----BEGINNING WITH PHASE: ', phase ) 
    print('\n\n-----EXPERIMENT LENGTH: ', experiment_length, 'MINUTES' ) 
    print('\n\n-----BLOCK LENGTH: ', block_length, 'MINUTES', '\n\n\n' ) 

    # determine how sample images will be ordered
    images = image_order_protocol(params) 
    
    # set up visual environment, calibrate subjects 
    experiment_window, genv, params, el_tracker = setup_eyelink_for_experiment(params) 	
    
    while run_experiment: 
         
	# determine which image to use in trial 
        i_image = images[i_trial] 

        # create single trial, evaluate performance, return trial data 
        trial_data = run_single_trial(experiment_window, genv, i_image, params)
        # aggregate data across trials 
        experiment_data = experiment_data.append(trial_data, ignore_index=True) 
        # for each trial, save cumulative data collected within experiment 
        experiment_data.to_csv(os.path.join(params['results_folder'], subject_id))  
        
        # print to terminal 
        if params['verbose']: print('...data saved for %s'%subject_id)
        print( '---------- EXPERIMENT DATA SHAPE', experiment_data.shape) 

        if (phase == 'practice') * (i_trial == n_practice_trials): 
            
            eyelink_functions.show_msg(params, experiment_window, genv, between_block_message)
            el_tracker.doTrackerSetup() 
            phase = 'experiment'
            block_starttime = time.time() 
            experiment_starttime = time.time() 

        elif phase == 'experiment':

            blocktime_elapsed = (time.time() - block_starttime)/60  
            experimenttime_elapsed = (time.time() - experiment_starttime)/60

            print( '\n time elapsed within block', blocktime_elapsed, 'within experiment', experimenttime_elapsed ) 

            if experimenttime_elapsed > experiment_length: 
                print( '\n\n\n\n\n EXPERIMENT TIME ELAPSED \n\n\n\n\n' ) 
                run_experiment = False
                eyelink_functions.show_msg(params, experiment_window, genv, 'Finished :D')
            elif blocktime_elapsed > block_length:
                print( '\n\n\n\n\n BLOCK TIME ELAPSED \n\n\n\n\n' )
                eyelink_functions.show_msg(params, experiment_window, genv, between_block_message)
                el_tracker.doTrackerSetup()
                block_starttime = time.time()
        
        i_trial += 1
        if i_trial >= len(images): 
            images = image_order_protocol(params)
            i_trial = 0 
        
    # begin termination protocols 
    eyelink_functions.terminate_task(experiment_window, genv, params) 
    # close experiment window 
    experiment_window.close()
    # close psychopy 
    core.quit()
