//
//  SuggestionViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 10/30/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit

class SuggestionViewController: UIViewController {

    var del = UIApplication.sharedApplication().delegate as AppDelegate
    var pageState: Int!
    @IBOutlet var segmentedControl : UISegmentedControl!
    @IBOutlet var suggestionName : UILabel!
    @IBOutlet var descriptionText : UILabel!
    @IBOutlet var routeText : UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        refreshUI()
        segmentedControl.selectedSegmentIndex = pageState
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func indexChanged(sender:UISegmentedControl) {
        switch segmentedControl.selectedSegmentIndex {
        case 0:
            if (pageState == 1) {
                performSegueWithIdentifier("routeToDescSegue", sender: self);
            } else if (pageState == 2) {
                performSegueWithIdentifier("assumptionsToDescSegue", sender: self);
            }
        case 1:
            if (pageState == 0) {
                performSegueWithIdentifier("descToRouteSegue", sender: self);
            } else if (pageState == 2) {
                performSegueWithIdentifier("assumptionsToRouteSegue", sender: self);
            }
        case 2:
            if (pageState == 0) {
                performSegueWithIdentifier("descToAssumptionsSegue", sender: self);
            } else if (pageState == 1) {
                performSegueWithIdentifier("routeToAssumptionsSegue", sender: self);
            }
        default:
            break
        }
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {
        if (segue.identifier != "suggestionBackSegue") {
            var vc = segue.destinationViewController as SuggestionViewController
            vc.pageState = segmentedControl.selectedSegmentIndex
        }
    }
    
    func refreshUI() {
        self.suggestionName.text = del.suggestionModel.getName()
        if (self.descriptionText != nil) {
            self.descriptionText.text = del.suggestionModel.getDesc()
        }
        if (self.routeText != nil) {
            self.routeText.text = del.suggestionModel.getRoute()
        }
    }
}