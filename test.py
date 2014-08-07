import numpy as np
import cv2
# hardcoded size of zero template...
WIDTH = 25
HEIGHT = 28
DIFF_METHOD = 'cv2.TM_CCOEFF_NORMED'
def load_resources():
    number_templates = []
    for i in range(0,10):
        number_templates.append(cv2.imread('smash_resources/' + str(i) + '.png', 1))
    return number_templates
        
def compare_with_previous(img1, img2, locations_found):
    # compare img1 with img2 and see if anything changed significantly in locations_found
    # if diff falls below diff_threshold, then percentage has changed
    diff_threshold = 0.9
    for location in locations_found:
        # location[0] is horizontal, location[1] is vertical 
        # but you need to index into image vertically then horizontally
        percent_1 = img1[location[1]:location[1] + HEIGHT, location[0]:location[0] + WIDTH]
        percent_2 = img2[location[1]:location[1] + HEIGHT, location[0]:location[0] + WIDTH]
        diff = cv2.matchTemplate(percent_1, percent_2, eval(DIFF_METHOD))[0][0]
        print "diff: " + str(diff)
        if diff < diff_threshold:
            return False
    return True

def match_to_number(candidate, number_templates):
    # try to match candidate to each image in number_templates
    prev_diff = float("-inf")
    for index, number in enumerate(number_templates):
        cur_diff = cv2.matchTemplate(candidate, number, eval(DIFF_METHOD))
        if cur_diff > prev_diff:
            max_diff = cur_diff
            max_idx = index
    # if there's something reasonably close, return that...
    if max_diff > 0.5:
        return max_idx
    # otherwise return -1
    return -1
            
def main():
    # if threshold greater than this, its a match
    # maybe should just take top two instead..
    threshold = 0.95

    cap = cv2.VideoCapture('falconDitto.mp4')
    # hardcode to find start of match now...should be able to find this programmatically
    for i in range(1, 1400):
        cap.read()    
    ret, frame = cap.read()

    # find where percentages are using template matching
    # load the zero template, use matchTemplate to find spots which are closest to it
    number_templates = load_resources()
    zero = number_templates[0]
    diff = cv2.matchTemplate(frame, zero, eval(DIFF_METHOD))
    # cv2.imshow('diff', diff)
    # locations_found is the places where we think the zeros are
    locations_found_unzipped = np.where(diff > threshold)
    locations_found = zip(locations_found_unzipped[1], locations_found_unzipped[0])
    # draw a rectangle around each location, using hardcoded values of size of percents
    for top_left in locations_found:
        print "top left: " + str(top_left)
        bottom_right = (top_left[0] + WIDTH, top_left[1] + HEIGHT)
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

    _, previous_frame = cap.read()
    while(cap.isOpened()):
        ret ,frame = cap.read()
        if ret == True:
            cv2.imshow('frame', frame)
            if not compare_with_previous(previous_frame, frame, locations_found):
                cv2.waitKey(0)
                # percentage will shake around, making it unstable
                # wait until stable again to look for difference between it and previous one
                cur_stability = False
            else: 
                cur_stability = True
            # if we've stabilized, check both percentages to see whats changed
            if cur_stability and not prev_stability:
                for idx, location in locations_found:
                    candidate = frame[location[1]:location[1] + HEIGHT, location[0]:location[0] + WIDTH]
                    best_guess = match_to_number(candidate, number_templates)
                    
                    
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break   
            prev_stability = cur_stability
        else:
            break
        previous_frame = frame
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()
