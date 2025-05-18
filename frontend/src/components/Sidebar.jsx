import React, { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import {
  HomeIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  TagIcon,
  Cog6ToothIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import { Link, useLocation } from 'react-router-dom';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Themes', href: '/themes', icon: TagIcon },
];

const secondaryNavigation = [
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  { name: 'Help', href: '/help', icon: QuestionMarkCircleIcon },
];

export default function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const location = useLocation();
  
  return (
    <>
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50 md:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </Transition.Child>

          <div className="fixed inset-0 z-50 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-4 pb-3 shadow-xl">
                <Transition.Child
                  as={Fragment}
                  enter="ease-in-out duration-300"
                  enterFrom="opacity-0"
                  enterTo="opacity-100"
                  leave="ease-in-out duration-300"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                >
                  <div className="absolute top-0 right-0 -mr-12 pt-2">
                    <button
                      type="button"
                      className="ml-1 flex h-8 w-8 items-center justify-center rounded-full focus:outline-none focus:ring-1 focus:ring-white"
                      onClick={() => setSidebarOpen(false)}
                    >
                      <span className="sr-only">Close sidebar</span>
                      <XMarkIcon className="h-5 w-5 text-white" aria-hidden="true" />
                    </button>
                  </div>
                </Transition.Child>
                <div className="flex flex-shrink-0 items-center px-3">
                  <svg className="h-5 w-5 text-sky-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                  <h1 className="ml-2 text-xs font-semibold text-sky-600">DocThemes</h1>
                </div>
                <div className="mt-4 flex-1 overflow-y-auto px-2">
                  <nav className="space-y-1">
                    {navigation.map((item) => {
                      const current = location.pathname === item.href;
                      return (
                        <Link
                          key={item.name}
                          to={item.href}
                          className={`group flex items-center px-2 py-1.5 text-xs font-medium rounded-md ${
                            current
                              ? 'bg-sky-100 text-sky-900'
                              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                          onClick={() => setSidebarOpen(false)}
                        >
                          <item.icon
                            className={`mr-2 h-3.5 w-3.5 flex-shrink-0 ${
                              current ? 'text-sky-600' : 'text-gray-400 group-hover:text-gray-500'
                            }`}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      );
                    })}
                  </nav>
                  <div className="mt-6">
                    <h3 className="px-2 text-xs font-medium text-gray-500" id="mobile-teams-headline">
                      Support
                    </h3>
                    <div className="mt-1 space-y-1" role="group" aria-labelledby="mobile-teams-headline">
                      {secondaryNavigation.map((item) => {
                        const current = location.pathname === item.href;
                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                            className={`group flex items-center px-2 py-1.5 text-xs font-medium rounded-md ${
                              current
                                ? 'bg-sky-100 text-sky-900'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                            onClick={() => setSidebarOpen(false)}
                          >
                            <item.icon
                              className={`mr-2 h-3.5 w-3.5 flex-shrink-0 ${
                                current ? 'text-sky-600' : 'text-gray-400 group-hover:text-gray-500'
                              }`}
                              aria-hidden="true"
                            />
                            {item.name}
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
            <div className="w-14 flex-shrink-0" aria-hidden="true">
            </div>
          </div>
        </Dialog>
      </Transition.Root>

      <div className="hidden md:fixed md:inset-y-0 md:flex md:w-56 md:flex-col">
        <div className="flex min-h-0 flex-1 flex-col border-r border-gray-200 bg-white shadow-sm">
          <div className="flex flex-1 flex-col overflow-y-auto pt-4 pb-3">
            <div className="flex flex-shrink-0 items-center px-3">
              <svg className="h-5 w-5 text-sky-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
              <h1 className="ml-2 text-xs font-semibold text-sky-600">DocThemes</h1>
            </div>
            <nav className="mt-4 flex-1 space-y-1 bg-white px-2">
              {navigation.map((item) => {
                const current = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-1.5 text-xs font-medium rounded-md ${
                      current
                        ? 'bg-sky-100 text-sky-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <item.icon
                      className={`mr-2 h-3.5 w-3.5 flex-shrink-0 ${
                        current ? 'text-sky-600' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                      aria-hidden="true"
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
            <div className="mt-4">
              <h3 className="px-3 text-xs font-medium text-gray-500" id="desktop-teams-headline">
                Support
              </h3>
              <div className="mt-1 space-y-1" role="group" aria-labelledby="desktop-teams-headline">
                {secondaryNavigation.map((item) => {
                  const current = location.pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`group flex items-center px-2 py-1.5 text-xs font-medium rounded-md ${
                        current
                          ? 'bg-sky-100 text-sky-900'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <item.icon
                        className={`mr-2 h-3.5 w-3.5 flex-shrink-0 ${
                          current ? 'text-sky-600' : 'text-gray-400 group-hover:text-gray-500'
                        }`}
                        aria-hidden="true"
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}