//
//  InterestsViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 11/5/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit

class InterestsViewController: UIViewController {
    @IBOutlet var backButton : UIButton!
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func returnToSettings() {
        performSegueWithIdentifier("settings", sender: self)
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {
        if (segue.identifier == "settings") {
            var vc = segue.destinationViewController as UITabBarController
            vc.tabBarController?.selectedIndex = 2
        }
    }
    
    
}

