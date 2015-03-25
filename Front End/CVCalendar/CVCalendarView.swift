//
//  CVCalendarView.swift
//  CVCalendar
//
//  Created by E. Mozharovsky on 12/26/14.
//  Copyright (c) 2014 GameApp. All rights reserved.
//

import UIKit

class CVCalendarView: UIView {
    
    // MARK: - Current date 
    var presentedDate: CVDate? {
        didSet {
            self.delegate?.presentedDateUpdated(self.presentedDate!)
        }
    }
    
    // MARK: - Calendar View Delegate
    
    var shouldShowWeekdaysOut: Bool? {
        if let delegate = self.delegate {
            return delegate.shouldShowWeekdaysOut()
        } else {
            return false
        }
    }
    
    @IBOutlet var calendarDelegate: AnyObject? {
        set {
            if let calendarDelegate: AnyObject = newValue {
                if calendarDelegate.conformsToProtocol(CVCalendarViewDelegate.self) {
                    self.delegate = calendarDelegate as? CVCalendarViewDelegate
                }
            }
        }
        
        get {
            return self.delegate
        }
    }
    
    var delegate: CVCalendarViewDelegate?
    
    // MARK: - Calendar Appearance Delegate
    
    @IBOutlet var calendarAppearanceDelegate: AnyObject? {
        set {
            if let calendarAppearanceDelegate: AnyObject = newValue {
                if calendarAppearanceDelegate.conformsToProtocol(CVCalendarViewAppearanceDelegate.self) {
                    self.appearanceDelegate?.delegate = calendarAppearanceDelegate as? CVCalendarViewAppearanceDelegate
                }
            }
        }
        
        get {
            return self.appearanceDelegate
        }
    }
    
    var appearanceDelegate: CVCalendarViewAppearance? = CVCalendarViewAppearance.sharedCalendarViewAppearance
    
    // MARK: - Calendar Animator Delegate
    
    @IBOutlet var animatorDelegate: AnyObject? {
        set {
            if let animatorDelegate: AnyObject = newValue {
                if animatorDelegate.conformsToProtocol(CVCalendarViewAnimatorDelegate.self) {
                    self.animator = animatorDelegate as? CVCalendarViewAnimatorDelegate
                }
            }
        }
        
        get {
            return self.animator
        }
    }
    
    var animator: CVCalendarViewAnimatorDelegate? = CVCalendarViewAnimator()
    
    // MARK: - Manual Setup
    
    var contentView: CVCalendarContentView?
    var monthViewHolder: UIView? {
        didSet {
            let width = self.monthViewHolder!.frame.width
            let height = self.monthViewHolder!.frame.height
            let x = CGFloat(0)
            let y = CGFloat(0)
            
            let frame = CGRectMake(x, y, width, height)
            
            let presentMonthView = CVCalendarMonthView(calendarView: self, date: NSDate())
            presentMonthView.updateAppearance(frame)
            self.contentView = CVCalendarContentView(frame: frame, calendarView: self, presentedMonthView: presentMonthView)
            self.monthViewHolder?.addSubview(self.contentView!)
        }
    }
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        
        self.monthViewHolder = self
        self.hidden = true
        let presentMonthView = CVCalendarMonthView(calendarView: self, date: NSDate())
        presentMonthView.updateAppearance(CGRectZero)
        self.contentView = CVCalendarContentView(frame: bounds, calendarView: self, presentedMonthView: presentMonthView)
        self.addSubview(self.contentView!)
    }
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        
        self.monthViewHolder = self
        self.hidden = true
        let presentMonthView = CVCalendarMonthView(calendarView: self, date: NSDate())
        presentMonthView.updateAppearance(frame)
        self.contentView = CVCalendarContentView(frame: bounds, calendarView: self, presentedMonthView: presentMonthView)
        self.addSubview(self.contentView!)
    }

    // IB Initialization
    required init(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
        
        self.monthViewHolder = self
        self.hidden = true
        let presentMonthView = CVCalendarMonthView(calendarView: self, date: NSDate())
        presentMonthView.updateAppearance(frame)
        self.contentView = CVCalendarContentView(frame: bounds, calendarView: self, presentedMonthView: presentMonthView)
        self.addSubview(self.contentView!)
    }
    
    // MARK: - Calendar View Control
    
    func changeDaysOutShowingState(shouldShow: Bool) {
        self.contentView!.updateDayViews(shouldShow)
    }
    
    func didSelectDayView(dayView: CVCalendarDayView) {
        self.contentView?.performedDayViewSelection(dayView)
        self.delegate?.didSelectDayView(dayView)
    }
    
    // MARK: - Final preparation
    
    // Called on view's appearing.
    func commitCalendarViewUpdate() {
        let width = self.monthViewHolder!.frame.width
        let height = self.monthViewHolder!.frame.height
        let x = CGFloat(0)
        let y = CGFloat(0)
        
        let coordinator = CVCalendarDayViewControlCoordinator.sharedControlCoordinator
        coordinator.animator = self.animator
        
        let frame = CGRectMake(x, y, width, height)
        self.contentView!.updateFrames(frame)
    }
    
    func toggleMonthViewWithDate(date: NSDate) {
        self.contentView!.togglePresentedDate(date)
    }
    
    func toggleTodayMonthView() {
        self.contentView!.togglePresentedDate(NSDate())
    }
    
    func loadNextMonthView() {
        self.contentView!.presentNextMonth(nil)
    }
    
    func loadPreviousMonthView() {
        self.contentView!.presentPreviousMonth(nil)
    }
}
